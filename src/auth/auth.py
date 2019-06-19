import re
import os, shutil
from src.auth import db

def check_signup(request):
    username = request.form['username']
    password = request.form['password']
    rpassword = request.form['rpassword']
    name = request.form['name']
    if password == rpassword and not db.check_user_exist(username):
        return (True,name,username,password)  # True for future use
    return (False,name,username,password)

def check_signin(request):
	username = request.form['username']
	password = request.form['password']
	return (username,password)

# check user is already logged in or not
# if logged in then who is he/she?
def check_session(session):
	if 'username' not in session or not db.check_user_exist(session['username']) :
		return (False,None)
	return (True,session['username'])

def add_username_session(username, session):
	session['username'] = username

def logout(session):
	session.pop('username',None)
	return (True, 1)