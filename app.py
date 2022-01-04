import re
from flask import Flask
from flask import request
from flask import redirect
from flask.wrappers import Response
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_socketio import (
  SocketIO,
  join_room,
  leave_room
)
from webargs import fields
from webargs.flaskparser import use_kwargs

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
PROXI_DOMAIN = 'https://127.0.0.1:5000'

#REGISTRATION EMAIL
with open('./register_verification.txt', 'r') as file:
    reg_ver_txt_file = file.read().replace('\n', '')
with open('./register_verification_html.txt', 'r') as file:
    reg_ver_html_file = file.read().replace('\n', '')

print("\n\n\n\n\n********** PLEASE VERIFY THAT PROXI DOMAIN IS CHANGED WHEN WEBSITE PUBLISHED **********\n\n\n\n\n")

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
    print(new_data)
    print(">>> Recieved message from {} on chat {}. CONTENT: {}".format(data["user_id"],data["chat_id"],data["content"]))
    socketio.emit('message', data, room=data['chat_id'])

@socketio.on('delete_message')
def on_new_message(data_json):
    data = json.loads(data_json)
    sqldb.del_msg(data["message_id"])

class Chats(Resource):
    def post(self, chat_id):
        chat_json = request.data
        chat_data=json.loads(chat_json)
        try:
          sqldb.add_chat(chat_data["chatName"], chat_data["coordinates"] ,chat_data["creatorId"], chat_data["description"])
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
          sqldb.edit_chat(chat_id, chat_data["name"], chat_data["creator_id"], chat_data["location"], chat_data["icon"]["filename"], chat_data["icon"]["content"], chat_data["description"])
        except Exception as err:
          print("Couldn't update data for chat {}: {}".format(chat_id, err))
          return {"success": False}

    def delete(self, chat_id):
        try:
          sqldb.del_chat(chat_id)
        except Exception as err:
          print("Couldn't get data for chat {}: {}".format(chat_id, err))
          return {"success": False}
class User(Resource):
    def post(self, user_id):
        user_data = json.loads(request.data)
        try:
          if sqldb.get_user_is_existing(user_data["email"]):
            return {"user_id": sqldb.get_user_though_email(user_data["email"]), "is_existing": True}
          sqldb.add_user(
            user_data["firstName"],
            user_data["lastName"],
            user_data["bio"],
            user_data["email"],
            user_data["profPicB64"],
            user_data["profPicFilePath"],
            user_data["birthday"],
          )
          time.sleep(100)
          return_string = {"user_id":sqldb.get_user_though_email(user_data["email"]), "is_existing": False}
          return json.dumps(return_string)
        except Exception as err:
          print("Couldn't understand POST request to user:",err)

    @use_kwargs({'email': fields.Str(missing='default_val')}, location="query")
    def get(self, user_id):
        try:
          sqldb.get_user(user_id)
        except Exception as err:
          print("Couldn't get data for user {}: {}".format(user_id, err))

    def put(self, user_id):
        user_json = request.data.decode("utf-8")
        user_data=json.loads(user_json)
        try:
          sqldb.edit_user(
            user_id,
            user_data["f_name"],
            user_data["s_name"],
            user_data["about_me"],
            user_data["email"],
            user_data["prof_pic"]["filename"],
            user_data["prof_pic"]["content"],
            user_data["birthday"], 
          )
        except Exception as err:
          print("Couldn't update data for user {}: {}".format(user_id, err))

    def delete(self, user_id):
        try:
          sqldb.del_user(user_id)
        except Exception as err:
          print("Couldn't delete user {}: {}".format(user_id, err))
class Messages(Resource):
    @use_kwargs({'hwmny': fields.Str(missing='default_val')}, location="query")
    def get(chat_id, hwmny):
        print(hwmny)
        try:
          temp_all = sqldb.get_msg_list_by_chat(chat_id)
          print(temp_all)
          #temp_return = []
          #for i in range(hwmny):
          #  print(temp_all[len(temp_all)-i])
          #  temp_return.append(temp_all[len(temp_all)-i])
          return temp_all#temp_return
        except:
          return {"messages":[{"content":"couldn't get messages", "user_id":1, "chat_id":1, "image":{"filename":"None", "content":"nonenoenoenoeneoneoenoenoeneoneneoineoneoneoneonenoene"}}]}
class Location(Resource):
    def get(self):
      points = json.loads(request.data)
      p1 = points["point1"]
      p2 = points["point2"]
      r = 6371
      distance =  2*r*math.asin(math.sqrt(math.sin(math.degrees((p2["lat"]-p1["lat"])/2))**2+(1-(math.degrees(math.sin((p2["lat"]-p1["lat"])/2)**2))-(math.degrees(math.sin((p2["lat"]+p1["lat"])/2)**2)))*(math.degrees(math.sin((p2["lng"]-p1["lng"])/2)**2))))
      print(distance)
      return {"distance": distance}
class VerifyUser(Resource):
    @use_kwargs({'email': fields.Str(missing='default_val'),'code': fields.Str(missing='default_val'),'origin': fields.Str(missing='default_val')}, location="query")
    def get(self, code, email, origin):
        ver_code = sqldb.check_confirmation_code(email)["code"][2]
        if str(code) == str(ver_code):
          sqldb.confirm_user(email, True)
          if origin == "email":
            return PROXI_DOMAIN
          if origin == "angular":
            return {"isCodeValid":True}
        elif code != ver_code:
          print(code, "CORRECT CODE", ver_code)
          return "Wrong code, please try again"

    @use_kwargs({'email': fields.Str(missing='default_val')}, location="query")
    def post(self, email):
      random_code_temp = random.randint(100000, 999999)
      sqldb.create_new_confirmation_code(email, random_code_temp)
      send_confirmation_of_email(email, EMAIL_PASSWORD, EMAIL_ADDRESS, PROXI_DOMAIN, random_code_temp)  
class GetUserId(Resource):
  @use_kwargs({'email': fields.Str(missing='default_val')}, location="query")
  def get(self, email):
        try:
          return sqldb.get_user_though_email(email)
        except Exception as err:
          print("Couldn't get ID for user with email {}: {}".format(email, err))
class GlobalVariables(Resource):
  @use_kwargs({'varname': fields.Str(missing='default_val')}, location="query")
  def get(varname):
    try:
      return {"variable":gVar[varname]}
    except:
      return {"variable": None}

  @use_kwargs({'varname': fields.Str(missing='default_val'), 'value': fields.Str(missing='default_val')}, location="query")
  def post(varname, value):
    try:
      gVar[varname] = value
    except:
      return {"success": False}

class RecentChats(Resource):
  def get(user_id):
    try:
      return sqldb.return_recent_chats_ids(user_id)
    except Exception as err:
          print("Couldn't get recent chats: {}".format(err))

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

def on_init():
  api.add_resource(Chats, '/api/chats/<int:chat_id>')
  api.add_resource(User, '/api/user/<int:user_id>')
  api.add_resource(Location, '/api/process/location')
  api.add_resource(Messages, '/api/get-messages/<int:chat_id>')
  api.add_resource(VerifyUser, '/api/verify')
  api.add_resource(GetUserId, '/api/get-user-id')
  api.add_resource(GlobalVariables, '/api/variables')
  api.add_resource(RecentChats, '/api/recent/<int:user_id>')

  chat_table_params = [
      "chat_id INT AUTO_INCREMENT",
      "PRIMARY KEY (chat_id)",
      "creator_id INT",
      "name TEXT", 
      "description TEXT", 
      "image_name TEXT",
      "image BLOB",
      "created_on DATETIME",
      "loc_latitude FLOAT",
      "loc_longitude FLOAT"]
  messages_table_params = [
      "message_id INT AUTO_INCREMENT",
      "PRIMARY KEY (message_id)",
      "sender_id INT",
      "chat_id INT",
      "message TEXT", 
      "image BLOB",
      "send_on DATETIME"]
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
      "birthday DATE",
      "created_on DATE"]
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
    "visited_on DATE",]

  gVar['chatNumber'] = sqldb.get_rows_num('chats')
  
  sqldb.drop_table("chats")
  sqldb.drop_table("messages")
  sqldb.drop_table("chat_usrs")
  sqldb.drop_table("users")
  sqldb.drop_table("users_email")
  sqldb.drop_table("users_visited")
  
  sqldb.gen_table("chats", chat_table_params)
  sqldb.gen_table("messages", messages_table_params)
  sqldb.gen_table("chat_usrs", chat_users_params)
  sqldb.gen_table("users", usrs_table_params)
  sqldb.gen_table("users_email", usrs_email_table_params) 
  sqldb.gen_table("users_visited", usrs_visited_chat_params) 

if __name__ == '__main__':
  on_init()
  app.run()