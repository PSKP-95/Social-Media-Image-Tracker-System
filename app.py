from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
from src.auth import auth,db

app = Flask(__name__)

app.secret_key = b'_ueh2434%8F4Q8z\n\xec]/'

@app.route('/',methods=['POST','GET'])
def index():
    id = 0
    if request.method == "GET":
        id = request.args.get("id")
    (flag, username) = auth.check_session(session)
    if id == None or id == 0:
        id = 0
    if flag:
        users,cur_user = db.get_users(username,id)
        messages = db.get_messages(username,id)
        return render_template('messaging/home.html',username=username,users=users,cur = cur_user,messages = messages)
    return redirect(url_for("login"), code=302)
    # return render_template("demo1.html")

@app.route('/login',methods=['POST','GET'])
def login():
    error = -1

    (flag, username) = auth.check_session(session)

    if request.method == "POST":
        username, password = auth.check_signin(request)
        if db.check_record(username, password):
            error = 1  # successful
            auth.add_username_session(username, session)
            (flag, username) = (True, username)
            print('[' + username + '] : ' + 'Logged In')
        else:
            error = 2  # wrong password / username
    if flag:
        return redirect(url_for("index"), code=302)

    return render_template("auth/login.html", error=error)

@app.route('/signup',methods=['POST','GET'])
def signup():
    error = -1
    if request.method == "POST":
        flag, name, username, password = auth.check_signup(request)
        if flag:
            if db.new_signup(username, name, password):
                error = 1
            else:
                error = 2  # user already exists
        else:
            error = 3  # wrong info
        return redirect(url_for("login"), code=302)
    return render_template("auth/signup.html", error=error)

@app.route('/logout',methods=['POST','GET'])
def logout():
    error = -1

    (flag, username) = auth.check_session(session)
    if flag:
        auth.logout(session)
        print('[' + username +'] : ' + 'Logged Out')

    return redirect(url_for("index"), code=302)

@app.route('/submit',methods=['POST','GET'])
def submit():
    (flag, username) = auth.check_session(session)
    if flag:
        status,cur = db.write_file(request,username)
        if status:
            users, cur_user = db.get_users(username)
            return redirect(url_for("index"), code=302)
    return "HIIII"

@app.route('/trace',methods=['POST','GET'])
def trace_it():
    (flag, username) = auth.check_session(session)
    if flag:
        flag, trace = db.get_trace(request, username)
        if flag:
            print(trace)
            trace2 = []
            for i in trace:
                i = i.split(' ')
                trace2.append(i)

            #trace = trace.split(' ')
            return render_template("messaging/trace.html",message = trace2,username=username)
        else:
            trace = ["Trace Failed"]
            print(trace)
            return render_template("messaging/trace.html", message=trace,username=username)
    return redirect(url_for("index"), code=302)

@app.route('/wiki',methods=['POST','GET'])
def wiki():
    return render_template("wiki/home.html")

@app.route('/wiki/problem',methods=['POST','GET'])
def problem():
    return render_template("wiki/problem.html")

@app.route('/wiki/steganography',methods=['POST','GET'])
def steganography():
    return render_template("wiki/steganography.html")

@app.route('/wiki/perceptual',methods=['POST','GET'])
def perceptual():
    return render_template("wiki/perceptual.html")

@app.route('/wiki/objective',methods=['POST','GET'])
def objective():
    return render_template("wiki/objective.html")

@app.route('/wiki/report',methods=['POST','GET'])
def report():
    return render_template("wiki/report.html")

@app.route('/wiki/synopsis',methods=['POST','GET'])
def synopsis():
    return render_template("wiki/synopsis.html")

@app.route('/wiki/conclusion',methods=['POST','GET'])
def conclusion():
    return render_template("wiki/conclusion.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
