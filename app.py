from datetime import datetime
import re
from flask import Flask
from flask import request
from flask import redirect
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
from marshmallow.fields import Float
from webargs import fields
from webargs.flaskparser import use_kwargs
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import smtplib, ssl

from werkzeug import datastructures
import sqldb 
import json
import random
import math
import time

with open("./globalVariables.json", "r") as f:
    gVar_total = json.load(f)
    gVar = gVar_total["flask_app_d"]

app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(
    app,
    origins="*",
    allow_headers=[
        "Content-Type", "Authorization",
        "Access-Control-Allow-Credentials"
    ],
    supports_credentials=True
)
app.config['SECRET_KEY'] = gVar["secret_key"]

#EMAIL
EMAIL_ADDRESS = 'noReplyProxi@gmail.com'
EMAIL_PASSWORD = 'proxiNoReply'
PROXI_DOMAIN = '192.168.18.14:5000'

#VAR
EARTH_RADIUS = 6371 #m

#REGISTRATION EMAIL
with open('./register_verification.txt', 'r') as file:
    reg_ver_txt_file = file.read().replace('\n', '')
with open('./register_verification_html.txt', 'r') as file:
    reg_ver_html_file = file.read().replace('\n', '')

#SOCKETIO
@socketio.on('join')
def on_join(data_jsonned):
    data = json.loads(data_jsonned)
    user_id = data['user_id']
    room = data['chat_id']
    user_data = sqldb.get_user(user_id)
    sqldb.add_visited_chat(user_id, room)
    join_room(room)

@socketio.on('leave')
def on_leave(data):
    data = json.loads(data)
    room = data['chat_id']
    leave_room(room)

@socketio.on('message')
def on_new_message(data_json):
    data = json.loads(data_json)
    new_message_id = sqldb.add_msg(
      data["chat_id"],
      data["content"],
      int(data["user_id"]),
      data["image"]["content"]
    )
    new_data = sqldb.get_msg_by_msg_id(new_message_id)
    socketio.emit('message', data, room=data['chat_id'])

@socketio.on('delete_message')
def on_new_message(data):
    sqldb.del_msg(data)


def get_distance_between(p1, p2):
      r = EARTH_RADIUS
      lon1, lat1, lon2, lat2 = map(math.radians, [p1["lat"], p1["lng"], p2["lat"], p2["lng"]])
      distance =  2*r*math.asin(math.sqrt(math.sin((lat2-lat1)/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2-lon1)/2)**2))
      return distance
def sendSMTP_mail(sender, password, receiver, message, email_use):
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender, password)
        server.sendmail(
            sender, receiver, message.as_string()
        )
    print("Send email to: {} {}".format(receiver, email_use))
def send_confirmation_of_email(reciever, password, sender_email, proxi_domain_base, code):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verification Code"
    message["From"] = sender_email
    message["To"] = reciever

    proxiHelpLink = proxi_domain_base + '/help'
    proxiCodeLink = proxi_domain_base + '/api/verify?email={}&code={}&origin={}'.format(reciever, code, "email")

    text_rendered = reg_ver_txt_file.format(proxiCodeLink, code, proxiHelpLink)
    html_rendered = reg_ver_html_file.format(proxiCodeLink, code, proxiHelpLink)

    part1 = MIMEText(text_rendered, "plain")
    part2 = MIMEText(html_rendered, "html")

    message.attach(part1)
    message.attach(part2)

    sendSMTP_mail(sender_email, password, reciever, message, 'VERIFICATION EMAIL. CODE => {}'.format(code))
def sendEmailFunc(email: str):
      random_code_temp = random.randint(100000, 999999)
      sqldb.create_new_confirmation_code(email, random_code_temp)
      send_confirmation_of_email(email, EMAIL_PASSWORD, EMAIL_ADDRESS, PROXI_DOMAIN, random_code_temp)
      return True 

def on_init():
  api.add_resource(Chats, '/api/chats/<int:chat_id>')
  api.add_resource(User, '/api/user/<int:user_id>')
  api.add_resource(Messages, '/api/get-messages/<int:chat_id>')
  api.add_resource(VerifyUser, '/api/verify')
  api.add_resource(GetUserIdThoughEmail, '/api/get-user')
  api.add_resource(GlobalVariables, '/api/variables')
  api.add_resource(RecentChats, '/api/recent/<int:user_id>')
  api.add_resource(IsUserVerified, '/api/is-verified/<int:user_id>')
  api.add_resource(GetNearMe, '/api/get-chats-near-me')
  api.add_resource(checkVerificationCode, '/api/check-if-correct-code')
  api.add_resource(GetChatsByUser, '/api/my-chats/<int:user_id>')

  chat_table_params = [
      "chat_id INT AUTO_INCREMENT",
      "PRIMARY KEY (chat_id)",
      "creator_id INT",
      "name TEXT", 
      "description TEXT", 
      "image_name TEXT",
      "image BLOB",
      "created_on TEXT",
      "loc_latitude FLOAT",
      "loc_longitude FLOAT",
      "radius FLOAT"]
  messages_table_params = [
      "message_id INT AUTO_INCREMENT",
      "PRIMARY KEY (message_id)",
      "sender_id INT",
      "chat_id INT",
      "message TEXT", 
      "image BLOB",
      "send_on TEXT"]
  chat_users_params = [
      "id INT AUTO_INCREMENT",
      "PRIMARY KEY (id)",
      "chat_id INT",
      "user_id INT"]
  usrs_table_params = [
      "user_id INT AUTO_INCREMENT",
      "PRIMARY KEY (user_id)",
      "f_name TEXT", 
      "s_name TEXT", 
      "bio TEXT", 
      "email TEXT",
      "prof_pic_filename TEXT",
      "prof_pic BLOB",
      "birthday TEXT",
      "created_on TEXT"]
  usrs_email_table_params = [
    "id INT AUTO_INCREMENT",
    "PRIMARY KEY (id)",
    "email TEXT",
    "confirmation_code INT",
    "confirmed_email BOOLEAN"]
  usrs_visited_chat_params = [
    "id INT AUTO_INCREMENT",
    "PRIMARY KEY (id)",
    "user_id INT",
    "chat_id INT",
    "visited_on TEXT",]
  usrs_passwords = []

  # sqldb.drop_table("chats")
  # sqldb.drop_table("messages")
  # sqldb.drop_table("chat_usrs")
  # sqldb.drop_table("users")
  # sqldb.drop_table("users_email")
  # sqldb.drop_table("users_visited")
  
  sqldb.gen_table("chats", chat_table_params)
  sqldb.gen_table("messages", messages_table_params)
  sqldb.gen_table("chat_usrs", chat_users_params)
  sqldb.gen_table("users", usrs_table_params)
  sqldb.gen_table("users_email", usrs_email_table_params) 
  sqldb.gen_table("users_visited", usrs_visited_chat_params) 

  gVar['chatNumber'] = sqldb.get_rows_num('chats')

class Chats(Resource):
    def post(self, chat_id):
        chat_json = request.data
        chat_data=json.loads(chat_json)
        try:
          sqldb.add_chat(chat_data["chatName"], chat_data["coordinates"] ,chat_data["creatorId"], chat_data["description"], chat_data["radius"])
          return {"success": True}
        except Exception as err:
          print("Couldn't understand POST request to chat:",err)
          return {"success": False,"error":err}

    def get(self, chat_id):
        try:
          return sqldb.get_chat_d(int(chat_id))
        except Exception as err:
          print("Couldn't get data for chat {}: {}".format(chat_id, err))
          return {"success": False}

    def put(self, chat_id):
        chat_json = request.data.decode("utf-8")
        chat_data=json.loads(chat_json)
        try:
          return {'success':sqldb.edit_chat(chat_id, chat_data["chatName"], chat_data["coordinates"], chat_data["description"], chat_data["radius"])}
        except Exception as err:
          print("Couldn't update data for chat {}: {}".format(chat_id, err))
          return {"success": False}

    def delete(self, chat_id):
        try:
          return {'success':sqldb.del_chat(chat_id)}
        except Exception as err:
          print("Couldn't get data for chat {}: {}".format(chat_id, err))
          return {"success": False}
class User(Resource):
    def post(self, user_id):
        user_data = json.loads(request.data)
        try:
          if sqldb.get_user_is_existing(user_data["email"]):
            print("This user already exists: {}".format(user_data["email"]))
            return json.dumps({"user_id": int(sqldb.get_user_id_though_email(user_data["email"])), "is_existing": True})
          print("This user doesn't exist. Creating new")
          sqldb.add_user(
            user_data["firstName"],
            user_data["lastName"],
            user_data["bio"],
            user_data["email"],
            user_data["profPicB64"],
            user_data["profPicFilePath"],
            str(user_data["birthday"]),
          )
          sendEmailFunc(user_data["email"])
          return_string = json.dumps({"user_id":sqldb.get_user_id_though_email(user_data["email"]), "is_existing": False})
          return return_string
        except Exception as err:
          print("Couldn't understand POST request to user:",err)

    def get(self, user_id):
        try:
          return sqldb.get_user(user_id)
        except Exception as err:
          print("Couldn't get data for user {}: {}".format(user_id, err))

    def put(self, user_id):
        user_json = request.data.decode("utf-8")
        user_data=json.loads(user_json)
        try:
          sqldb.edit_user(
            user_id,
            user_data["firstName"],
            user_data["lastName"],
            user_data["bio"],
            user_data["email"],
            user_data["profPicB64"],
            user_data["profPicFilePath"],
            str(user_data["birthday"]), 
          )
          return {'success':True}
        except Exception as err:
          print("Couldn't update data for user {}: {}".format(user_id, err))
          return {'success':False}

    def delete(self, user_id):
        try:
          sqldb.update_chat_owner(user_id, 3)
          sqldb.del_recent(user_id)
          return {'success': sqldb.del_user(user_id)}
        except Exception as err:
          print("Couldn't delete user {}: {}".format(user_id, err))
          return {'success': False}         
class Messages(Resource):
    @use_kwargs({'hwmny': fields.Str(missing='default_val')}, location="query")
    def get(self, chat_id, hwmny):
        try:
          temp_all = sqldb.get_msg_list_by_chat(int(chat_id))
          return temp_all
        except Exception as err:
          print(err)
          return json.dumps({"messages":[{"content":"couldn't get messages", "user_id":1, "chat_id":1, "image":{"filename":"None", "content":"nonenoenoenoeneoneoenoenoeneoneneoineoneoneoneonenoene"}}]})    
class VerifyUser(Resource):
    @use_kwargs({'email': fields.Str(missing='default_val'),'code': fields.Str(missing='default_val'),'origin': fields.Str(missing='default_val')}, location="query")
    def get(self, code, email, origin):
        ver_code = sqldb.check_confirmation_code(email)["code"][2]
        if str(code) == str(ver_code):
          sqldb.confirm_user(email, True)
          if origin == "email":
            return str(PROXI_DOMAIN)
          if origin == "angular":
            return {"isCodeValid":True}
        elif code != ver_code:
          return "Wrong code, please try again"
    def post(self):
      try:
        user_data = json.loads(request.data.decode('utf-8'))
        return {'success': sendEmailFunc(user_data['email'])}
      except Exception as err:
        print(err)
        return {"success": False}
class GetUserIdThoughEmail(Resource):
  @use_kwargs({'email': fields.Str(missing='default_val')}, location="query")
  def get(self, email):
        try:
          user_id = sqldb.get_user_id_though_email(email)
          return_data = sqldb.get_user(user_id)
          return return_data
        except Exception as err:
          print("Couldn't get ID for user with email {}: {}".format(email, err))
class GlobalVariables(Resource):
  @use_kwargs({'varname': fields.Str(missing='default_val')}, location="query")
  def get(self, varname):
    try:
      return {"variable":gVar[varname]}
    except:
      return {"variable": None}

  @use_kwargs({'varname': fields.Str(missing='default_val'), 'value': fields.Str(missing='default_val')}, location="query")
  def post(self, varname, value):
    try:
      gVar[varname] = value
    except:
      return {"success": False}
class RecentChats(Resource):
  def get(self, user_id):
    try:
      list_of_id = sqldb.return_recent_chats_ids(user_id)
      return_list = []
      for i in range(len(list_of_id["ids"])):
        data = sqldb.get_chat_d(list_of_id["ids"][i])
        return_list.append(data)
      return {'ids':return_list}
    except Exception as err:
        print("Couldn't get recent chats: {}".format(err))
class GetNearMe(Resource):
    @use_kwargs({'lat': fields.Str(missing='default_val'),'lng': fields.Str(missing='default_val')}, location="query")
    def get(self, lat, lng):
      chat_list = sqldb.get_chat_list(None)
      return_list = []
      p1 = {"lat":float(lat), "lng":float(lng)}
      for i in range(len(chat_list)):
        p2 = {"lat":chat_list[i]["loc_latitude"], "lng":chat_list[i]["loc_longitude"]}
        if float(get_distance_between(p1, p2))*1000<float(chat_list[i]["radius"]):
          return_list.append(chat_list[i])
      return return_list
class IsUserVerified(Resource):
  def get(self, user_id):
    return sqldb.check_is_user_valid(sqldb.get_user(user_id)['email'])
class checkVerificationCode(Resource):
  @use_kwargs({'code': fields.Str(missing='default_val'), 'email': fields.Str(missing='default_val')}, location="query")
  def get(self, code, email):
    if(int(code) == int(sqldb.check_confirmation_code(email)['code'])):
      sqldb.confirm_user(email, True)
      time.sleep(0.1)
      return {'validityOfCode':True}
    if(int(code) != int(sqldb.check_confirmation_code(email)['code'])):
      return {'validityOfCode':False}
class GetChatsByUser(Resource):
  def get(self, user_id):
        try:
          return sqldb.get_chat_list(user_id)
        except Exception as err:
          print("Couldn't get chats for use: {}".format(err))
if __name__ == '__main__':
  on_init()
  app.run(host='0.0.0.0')
