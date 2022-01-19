import re
from unicodedata import ucd_3_2_0
import mysql.connector
import json
import datetime

with open("./globalVariables.json", "r") as f:
    gVar_total = json.load(f)
    gVar = gVar_total["db_d"] 

mydb = mysql.connector.connect(
  host=gVar["host"],
  user=gVar["user"],
  password=gVar["password"],
  database=gVar["dbname"],
  port=gVar["port"]
)

dbcursor = mydb.cursor(buffered=True)

# TO START SQL SERVICE: LOOK UP SERVICES. FIND MYSQL SERVICE. START

def gen_table(dbname, params):
    try:
        i = 0
        params_string = ""
        for i in range(len(params)):
            params_string = params_string + params[i]
            if i < len(params)-1:
                params_string += ", "
            i+=1
        sql = ("CREATE TABLE IF NOT EXISTs {} ({})".format(dbname, params_string))
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Couldn't create database: {}".format(err))

def drop_table(name):
    try:
        sql = "DROP TABLE IF EXISTS {}".format(name)
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Couldn't drop table: {}".format(err))

#CHATS
def get_rows_num(table):
    query = "SELECT COUNT(*) from `%s`" %table
    dbcursor.execute(query)
    res = dbcursor.fetchone()
    return res[0]

def add_chat(name, location, creator_id, description, radius, image_name=None, image=None):
    try:
        sql = "INSERT INTO chats (name, creator_id, description, image_name, image, created_on, loc_latitude, loc_longitude, radius) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (name, int(creator_id), str(description), image_name, image, str(datetime.datetime.now()), location["lat"], location["lng"], radius)
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Couldn't create chat: {}".format(err))

def edit_chat(chat_id, name, location, description, radius, image_name=None, image=None):
    try:
        sql = "UPDATE chats SET name=%s, description=%s, image_name=%s, image=%s, loc_latitude=%s, loc_longitude=%s, radius=%s where chat_id = {}".format(chat_id)
        val = (name, str(description), image_name, image, location["lat"], location["lng"], radius)
        dbcursor.execute(sql, val)
        mydb.commit()
        return True
    except Exception as err:
        print("Couldn't edit chat: {}".format(err))
        return False

def del_chat(chat_id):
    try:
        sql = "DELETE FROM chats WHERE chat_id = {}".format(chat_id)
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Error: {}. Check if chat_id exists".format(err))

def get_chat_list(user_id):
    try:
        query_temp = ''
        if user_id != None or 0:
            query_temp = 'WHERE creator_id = {}'.format(user_id)
        dbcursor.execute("SELECT * FROM chats {}".format(query_temp))
        result = dbcursor.fetchall()
        return_dict = []
        for i in range(len(result)-1):
            chat_json = {
                "chat_id":result[i][0],
                "creator_id":result[i][1],
                "name":result[i][2],
                "description":result[i][3],
                "image":str(result[i][4]),
                "created_on":result[i][6],
                "loc_latitude":result[i][7],
                "loc_longitude":result[i][8],
                "radius":result[i][9]
            }
            return_dict.append(chat_json)
        return return_dict
    except Exception as err:
        print("Couldn't get data for chats: {}".format(err))

def get_chat_d(chat_id):
    try:
        dbcursor.execute("SELECT * FROM chats WHERE chat_id = {}".format(chat_id))
        result = dbcursor.fetchone()
        chat_json = {
            "chat_id":result[0],
            "creator_id":result[1],
            "name":result[2],
            "description":result[3],
            "image":str(result[4]),
            "created_on":result[6],
            "loc_latitude":result[7],
            "loc_longitude":result[8],
            'radius':result[9]
        }
        return chat_json
    except Exception as err:
        print("Couldn't get data for chat: {}".format(err))

#MESSAGES
def get_msg_by_msg_id(message_id):
    try:
        dbcursor.execute("SELECT * FROM messages WHERE message_id = {}".format(message_id))
        result = dbcursor.fetchall()
        return result
    except Exception as err:
        print("Couldn't get data for message through message id: {}".format(err))

def get_msg_list_by_chat(chat_id):
    try:
        dbcursor.execute("SELECT * FROM messages WHERE chat_id = {}".format(chat_id))
        result = dbcursor.fetchall()
        processed_result = []
        for i in range(len(result)-1):
            dict_result = {
                "messageId": result[i-1][0],
                "senderId": result[i-1][1],
                "chatId": result[i-1][2],
                "content": result[i-1][3],
                "sendOn": result[i-1][5],
                "imageB64": str(result[i-1][4])
            }
            processed_result.append(dict_result)
        return processed_result
    except Exception as err:
        print("Couldn't get messages by chat id: {}".format(err))

def get_msg_list_by_user(user_id):
    try:
        dbcursor.execute("SELECT * FROM messages WHERE user_id = {}".format(user_id))
        result = dbcursor.fetchall()
        return result
    except Exception as err:
        print("Couldn't get messages by user id: {}".format(err))

def add_msg(chat_id, msg, sender_id, img=None):
    try:
        sql = "INSERT INTO messages (chat_id, message, image, send_on, sender_id) VALUES (%s, %s, %s, %s, %s)"
        val = (chat_id, str(msg), img, str(datetime.datetime.now()), sender_id)
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Error couldn't add message: {}".format(err))

def del_msg(msg_id):
    try:
        sql = "DELETE FROM messages WHERE message_id = {}".format(msg_id)
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Error: {}. Check if message_id exists".format(err))

#USERS

def add_user(f_name, s_name, bio, email, pic_name, prof_pic, birthday):
    try:
        sql = "INSERT INTO users (f_name, s_name, bio, email, prof_pic_filename, prof_pic, birthday, created_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (f_name, s_name, bio, email, pic_name, prof_pic, birthday, str(datetime.datetime.now()))
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Error couldn't add user: {}".format(err))

def get_user(user_id):
    try:
        dbcursor.execute("SELECT * FROM users WHERE user_id = {}".format(user_id))
        result = dbcursor.fetchone()
        user_json = {
            "user_id":result[0],
            "f_name":result[1],
            "s_name":result[2],
            "description":result[3],
            "email":result[4],
            "prof_pic":str(result[5]),
            "prof_pic_filename":str(result[6]),
            "birthday":str(result[7]),
            "created_on":str(result[8]),
        }
        return user_json
    except Exception as err:
        print("Couldn't get data for user: {}".format(err))

def get_user_is_existing(email):
    try:
        dbcursor.execute("SELECT count(*) FROM users WHERE email = '{}'".format(email))
        is_existing = False
        temp = dbcursor.fetchone()[0]
        if temp>0:
            is_existing=True
        return is_existing
    except Exception as err:
        print("Couldn't get data wheather user is existing or not: {}".format(err))

def get_user_id_though_email(email):
    try:
        sql = "SELECT user_id FROM users WHERE email = '{}'".format(email)
        dbcursor.execute(sql)
        mydb.commit()
        myresult = dbcursor.fetchone()
        return myresult[0]
    except Exception as err:
        print("Couldn't get confirmation code: {}".format(err)) 


def del_user(user_id):
    try:
        sql = "DELETE FROM users WHERE user_id = {}".format(user_id)
        dbcursor.execute(sql)
        mydb.commit()
        return True
    except Exception as err:
        print("Error, please check user exists: {}".format(err))
        return False

def edit_user(user_id, f_name, s_name, bio, email, filename, prof_pic, birthday):
    try:
        sql = "UPDATE users SET f_name=%s, s_name=%s, bio=%s, email=%s, prof_pic_filename=%s, prof_pic=%s, birthday=%s WHERE user_id = {}".format(user_id)
        val = (f_name, s_name, str(bio), str(email), filename, prof_pic, str(birthday))
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Couldn't edit user: {}".format(err))

def confirm_user(email, is_confirmed):
    temp = 0
    if is_confirmed:
        temp = 1
    elif not is_confirmed:
        temp = 0
    try:
        sql = "UPDATE users_email SET confirmed_email = {} where email = '{}'".format(temp,email)
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Couldn't update confirmation of email: {}".format(err))

def create_new_confirmation_code(email, code):
    try:
        sql = "DELETE FROM users_email WHERE email LIKE '%{}%'".format(email)
        dbcursor.execute(sql)
        mydb.commit()
        sql = "INSERT INTO users_email (email, confirmation_code, confirmed_email) VALUES ('{}', {}, {})".format(email, code, 0)
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Error: {}".format(err))

def check_confirmation_code(email):
    try:
        sql = "SELECT confirmation_code FROM users_email WHERE email = '{}'".format(email)
        dbcursor.execute(sql)
        mydb.commit()
        myresult = dbcursor.fetchone()
        return {"code":myresult[0]}
    except Exception as err:
        print("Couldn't get confirmation code: {}".format(err))

def check_is_user_valid(email):
    try:
        sql = "SELECT confirmed_email FROM users_email WHERE email = '{}'".format(email)
        dbcursor.execute(sql)
        mydb.commit()
        myresult = dbcursor.fetchone()
        return {"isValid":bool(myresult)}
    except Exception as err:
        print("Couldn't get confirmation code: {}".format(err)) 

def add_visited_chat(user_id, chat_id):
    try:
        sql = "INSERT INTO users_visited (chat_id, user_id, visited_on) VALUES (%s, %s, %s)"
        val = (chat_id, user_id, str(datetime.datetime.now()))
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Error: {}".format(err))

def return_recent_chats_ids(user_id):
    try:
        sql = "SELECT DISTINCT chat_id FROM users_visited WHERE user_id = {}".format(user_id)
        dbcursor.execute(sql)
        mydb.commit()
        myresult = dbcursor.fetchall()
        temp = []
        for i in range(len(myresult)):
            temp.append(myresult[i][0])
        return {"ids":temp}
    except Exception as err:
        print("Couldn't get recent chats: {}".format(err))