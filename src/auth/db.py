import os

import pymysql, hashlib
from werkzeug import secure_filename

from src.logic import op
import numpy as np

from datetime import datetime


def connection():
	conn = pymysql.connect('localhost','root','pskp@a95a','whatsapp')
	cur = conn.cursor()
	return (conn,cur)

def get_SHA256(password):
	encoded = password.encode('utf-8')
	hash_object = hashlib.sha256(encoded)
	password = hash_object.hexdigest()
	return password
#
def check_record(username,password):
	conn,cur = connection()
	sql = """SELECT * FROM users where username = %s and password = %s"""

	password = get_SHA256(password)

	args = (username,password)
	cur.execute(sql,args)
	data = cur.fetchall()
	if(len(data)>0):
		print("[src.db.check_record] : Record Found")
		return True
	return False

def check_user_exist(username):
	conn, cur = connection()
	sql = """SELECT * FROM users where username = %s"""
	args = (username)

	cur.execute(sql,args)
	data = cur.fetchall()
	if(len(data)>0):
		print("[src.db.check_user_exist] : User Exists")
		return True
	return False


# new user adding to db
def new_signup(username, name, password):
    if check_user_exist(username):
        return False

    conn, cur = connection()

    sql = """insert into users(username,name,password) values(%s,%s,%s)"""

    password = get_SHA256(password)

    args = (username,name,password)

    cur.execute(sql,args)


    sql = "Create table " + username + "(other int(1),message varchar(500),flag int(1));"
    cur.execute(sql)
    # if you are writing to db then commit and close required
    conn.commit()
    conn.close()

    return True


def get_users(username,id=0):
    conn, cur = connection()

    sql = """select username,name,id from users where username != %s;"""
    args = (username)
    cur.execute(sql,args)
    data = cur.fetchall()
    users = []
    for i in data:
        if i[2] == int(id):
            users.append((i[0],i[1],i[2],True))
            cur_user = [i[0],i[1],i[2]]
        else:
            users.append((i[0], i[1], i[2], False))
    return (users,cur_user)

def get_users_2(username):
    print("get_users_2")
    conn, cur = connection()

    sql = """select username,name,id from users where username != %s;"""
    args = (username)
    cur.execute(sql,args)
    data = cur.fetchall()
    users = []
    for i in data:
        users.append((i[0], i[1], i[2], False))
    return (users)

def get_trace(request, username):
    print("write_file")
    try:
        f = request.files['img']
        filename = secure_filename(f.filename)
        time = list(str(datetime.now()).split(' '))
        time = time[0] + time[1]
        time = time.replace(':', '-')

        path1 = "static/uploads/" + time + "-" + filename
        f.save(path1)

        flag, text = op.decode(path1)
        if not flag:
            hash = op.dHash(path1)
            (flag, path2) = compare_hashes(hash)
            if flag:
                paths = []
                for pathx in path2:
                    flag, text = op.decode(pathx)
                    paths.append(text)
                return (flag,paths)
        else:
            print("Steganographic Trace Found")
        text = [text]
        return (flag,text)
    except Exception as e:
        print(e)
        return (False,'')

def write_file(request,username):
    print("write_file")
    try:
        f = request.files['data']
        filename = secure_filename(f.filename)

        time = list(str(datetime.now()).split(' '))
        time = time[0] + time[1]
        time = time.replace(':','-')

        path1 = "static/uploads/" + time + ".png"
        f.save(path1)
        path = "uploads/" + time + ".png"

        flag,text = op.decode(path1)
        act_text = ""
        if not flag :
            hash = op.dHash(path1)
            (flag, path2) = compare_hashes(hash)
            length = 0
            print(path2)
            if flag:
                for i in path2:
                    pathx = i
                    flag,text = op.decode(pathx)
                    text_path = text.split(' ')
                    print(text_path)
                    if length < len(text_path):
                        print("Accepted")
                        act_text = text
                        length = len(text_path)
            add_to_hashes(hash,path1)
        else:
            hash = op.dHash(path1)
            add_to_hashes(hash, path1)
        if act_text != "":
            text = act_text
        text_list = text.split(' ')
        if text_list[-1] != username:
            text += username + " "

        length = len(text)
        op.encode(path1,text,length)

        cur = request.form['receiver']
        update_db(cur,username,path)
        return (True, cur)
    except Exception as e:
        print(e)
        return (False,-1)

def compare_hashes(hash):
    print("[src.logic.op.compare_hashes]")
    conn, cur = connection()

    sql = """select image,hash from hashes;"""
    cur.execute(sql)
    data = cur.fetchall()

    min_dist = 1
    path = []
    print("*** Comparing Hashes ***")
    for i in data:
        hash_ = np.array(list(map(int,i[1].split())))
        dist = op.hamming_distance(hash_,hash)
        print(i[0] + " - " + str(dist))
        if dist < 0.1:
            path.append(i[0])
    if len(path) > 0:
        return (True,path)
    return (False, path)

def add_to_hashes(hash,path):
    print("[src.logic.op.add_to_hashes]")
    conn, cur = connection()

    text_hash = ""
    for i in hash:
        text_hash += str(i) + ' '
    text_hash = text_hash[:-1]

    sql = """insert into hashes(image,hash) values(%s,%s)"""

    args = (path,text_hash)

    cur.execute(sql, args)

    conn.commit()
    conn.close()


def find_users_from_id(id):
    print("find_users_from_id")
    conn, cur = connection()

    sql = "select username,id from users where id = " + id + ";"

    cur.execute(sql)
    data = cur.fetchall()
    for i in data:
        user = i
    return (user)

def find_users_from_username(username):
    print("find_users_from_username")

    conn, cur = connection()

    sql = """select username,id from users where username = %s;"""
    args = (username)
    cur.execute(sql, args)
    data = cur.fetchall()
    for i in data:
        user = i
    return (user)

def update_db(id,username,path):
    print("update_db")

    user1,id1 = find_users_from_id(id)
    user2, id2 = find_users_from_username(username)

    conn, cur = connection()

    # flag 1 == received
    # flag 0 == sent
    sql1 = "insert into " + user1 + "(other,message,flag) values(" + str(id2) +",'" + path + "'," + str(1) + ")"
    sql2 = "insert into " + user2 + "(other,message,flag) values(" + str(id1) +",'" + path + "'," + str(0) + ")"

    cur.execute(sql1)
    cur.execute(sql2)

    conn.commit()
    conn.close()

def get_messages(username,id=0):
    conn, cur = connection()

    sql = "select message,flag from " + username +" where other = " + str(id) +";"

    cur.execute(sql)
    data = cur.fetchall()
    messages = []
    for i in data:
        messages.append((i[0], i[1]))
    return (messages)