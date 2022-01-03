import mysql.connector
import json
import datetime

with open("C:/Users/nicol/OneDrive/Documents/Coding/Other/Proxi Website/backend/globalVariables.json", "r") as f:
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

def add_chat(name, location, creator_id, description, image_name=None, image=None):
    try:
        sql = "INSERT INTO chats (name, creator_id, description, image_name, image, created_on, loc_latitude, loc_longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (name, int(creator_id), str(description), image_name, image, datetime.datetime.now(), location["lat"], location["lng"])
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Couldn't create chat: {}".format(err))


def edit_chat(chat_id, name, creator_id, location, image_name, image, description):
    try:
        sql = "UPDATE chats SET (name, creator_id, description, image_name, image, loc_latitude, loc_longitude) VALUES (%s, %s, %s, %s, %s, %s, %s) where chat_id = {}".format(chat_id)
        val = (name, int(creator_id), str(description), image_name, image, location["lat"], location["lng"])
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Couldn't create chat: {}".format(err))

def del_chat(chat_id):
    try:
        sql = "DELETE * FROM chats WHERE chat_id = {}".format(chat_id)
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Error: {}. Check if chat_id exists".format(err))

def get_chat_list():
    try:
        dbcursor.execute("SELECT * FROM chats")
        result = dbcursor.fetchall()
        return result
    except Exception as err:
        print("Couldn't get data: {}".format(err))

def get_chat_d(chat_id):
    try:
        dbcursor.execute("SELECT * FROM chats WHERE chat_id {}".format(chat_id))
        result = dbcursor.fetchone()
        chat_json = {
            "chat_id":result[0],
            "creator_id":result[2],
            "name":result[3],
            "description":result[4],
            "image":result[6],
            "created_on":result[7],
            "loc_latitude":result[8],
            "loc_longitude":result[9],
        }
        return chat_json
    except Exception as err:
        print("Couldn't get data: {}".format(err))

#MESSAGES

def get_msg_list_by_chat(chat_id):
    try:
        dbcursor.execute("SELECT * FROM messages WHERE chat_id {}".format(chat_id))
        result = dbcursor.fetchall()
        return result
    except Exception as err:
        print("Couldn't get data: {}".format(err))

def get_msg_list_by_user(user_id):
    try:
        dbcursor.execute("SELECT * FROM messages WHERE user_id {}".format(user_id))
        result = dbcursor.fetchall()
        return result
    except Exception as err:
        print("Couldn't get data: {}".format(err))

def add_msg(chat_id, msg, sender_id, img=None):
    try:
        sql = "INSERT INTO messages (chat_id, message, image, send_on, sender_id) VALUES (%s, %s, %s, %s, %s)"
        val = (chat_id, str(msg), img, datetime.datetime.now(), sender_id)
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Error: {}".format(err))

def del_msg(msg_id):
    try:
        sql = "DELETE * FROM messages WHERE message_id = {}".format(msg_id)
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Error: {}. Check if message_id exists".format(err))

#USERS

def add_user(f_name, s_name, bio, email, pic_name, prof_pic, birthday):
    try:
        sql = "INSERT INTO users (f_name, s_name, bio, email, prof_pic_filename, prof_pic, birthday, created_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (f_name, s_name, bio, email, pic_name, prof_pic, birthday, datetime.datetime.now())
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Error: {}".format(err))

def get_user(user_id):
    try:
        dbcursor.execute("SELECT * FROM users WHERE user_id {}".format(user_id))
        result = dbcursor.fetchone()
        user_json = {
            "user_id":result[0],
            "f_name":result[1],
            "s_name":result[2],
            "description":result[3],
            "email":result[4],
            "prof_pic":result[5],
            "birthday":result[6],
            "created_on":result[7],
        }
        return user_json
    except Exception as err:
        print("Couldn't get data: {}".format(err))

def get_user_though_email(email):
    try:
        dbcursor.execute("SELECT * FROM users WHERE email '{}'".format(email))        
        return dbcursor.fetchone()[0]
    except Exception as err:
        print("Couldn't get data: {}".format(err))

def del_user(user_id):
    try:
        sql = "DELETE * FROM users WHERE user_id = {}".format(user_id)
        dbcursor.execute(sql)
        mydb.commit()
    except Exception as err:
        print("Error, please check user exists: {}".format(err))

def edit_user(user_id, f_name, s_name, bio, email, filename, prof_pic, birthday):
    try:
        sql = "UPDATE users SET (f_name, s_name, bio, email, prof_pic_filename, prof_pic, birthday) VALUES (%s, %s, %s, %s, %s, %s, %s) where user_id = {}".format(user_id)
        val = (f_name, s_name, str(bio), str(email), filename, prof_pic, str(birthday))
        dbcursor.execute(sql, val)
        mydb.commit()
        sql = "UPDATE users_email SET (email, confirmed_email) VALUES (%s, %s) where email = {}".format(email)
        val = (email, 0)
        dbcursor.execute(sql, val)
        mydb.commit()
    except Exception as err:
        print("Couldn't edit user: {}".format(err))

def confirm_user(email, is_confirmed):
    if is_confirmed:
        temp = 1
    elif not is_confirmed:
        temp = 0
    try:
        sql = "UPDATE users_email SET (confirmed_email) VALUES ({}) where email = '{}'".format(temp,email)
        val = (email)
        dbcursor.execute(sql, val)
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
        return {"code":myresult}
    except Exception as err:
        print("Couldn't get confirmation code: {}".format(err))
