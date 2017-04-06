# `University` VARCHAR(45) NULL),
# `Thesis_title` VARCHAR(450) NULL),
# `Funding_source` VARCHAR(145) NULL),
# `Start_date` VARCHAR(45) NULL),
# `Expected_finish_date` VARCHAR(45) NULL),
# `Supervisor` VARCHAR(45) NULL),
# `Thesis_submission_date` VARCHAR(45) NULL),
# `Student_mentor` VARCHAR(45) NULL)''')

from flask import Flask, render_template, json, request, session, redirect
from werkzeug import generate_password_hash, check_password_hash
import sqlite3, collections

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
# cursor.execute('SELECT * FROM tbl_user')

try:
    print 'creating user table'
    cursor.execute('''CREATE TABLE tbl_user
             (`user_name` VARCHAR(45) NULL UNIQUE,
             `user_username` VARCHAR(45) NULL,
             `user_password` VARCHAR(45) NULL)''')
except Exception as e:
        print e

try:
    print 'creating info table'
    cursor.execute('''CREATE TABLE tbl_info
             (`user_name` VARCHAR(45) UNIQUE NULL,
             `Email_address` VARCHAR(45) NULL,
             `University` VARCHAR(45) NULL,
             `Thesis_title` VARCHAR(450) NULL,
             `Funding_source` VARCHAR(145) NULL,
             `Start_date` VARCHAR(45) NULL,
             `Expected_finish_date` VARCHAR(45) NULL,
             `Supervisor` VARCHAR(45) NULL,
             `Thesis_submission_date` VARCHAR(45) NULL,
             `Student_mentor` VARCHAR(45) NULL)''')
except Exception as e:
        print e

try:
    print 'creating lectures table'
    cursor.execute('''CREATE TABLE tbl_lectures
             (`user_name` VARCHAR(45) UNIQUE NULL,
             `Lecture_course` VARCHAR(45) NULL,
             `Attendance` VARCHAR(45) NULL,
             `Record` VARCHAR(450) NULL)''')
except Exception as e:
        print e

try:
    print 'creating skills table'
    cursor.execute('''CREATE TABLE tbl_skills
             (`user_name` VARCHAR(45) UNIQUE NULL,
             `Skill` VARCHAR(45) NULL)''')
except Exception as e:
        print e

try:
    print 'creating assessments table'
    cursor.execute('''CREATE TABLE tbl_assessments
             (`user_name` VARCHAR(45) NULL UNIQUE,
             `Assessment` VARCHAR(45) NULL,
             `Result` VARCHAR(45) NULL)''')
except Exception as e:
        print e

def sp_createUser(username, email, password):
    t = (username,)
    cursor.execute('SELECT rowid FROM tbl_user WHERE user_name = ?', t)
    data = cursor.fetchone()
    if data is None:
        t = (username,email,password,)
        print 't = ', t
        cursor.execute('INSERT INTO tbl_user VALUES (?,?,?)', t)
        conn.commit()
        return True
    else:
        return False

def sp_validateLogin(username):
    t = (username,)
    cursor.execute('SELECT * FROM tbl_user WHERE user_username = ?', t)
    return cursor.fetchall()

def sp_getStudentInfo(username):
    t = (username,)
    cursor.execute('SELECT * FROM tbl_user WHERE user_name = ?', t)
    data = cursor.fetchone()
    studentInfo = list()
    studentInfo.append({'title': 'Name', 'value': data[0]})
    studentInfo.append({'title': 'Email Address', 'value': data[1]})
    print 'studentInfo = ', studentInfo
    cursor.execute('SELECT * FROM tbl_info WHERE user_name = ?', t)
    data = cursor.fetchone()
    if data == None:
        data = ('None','None','None','None','None','None','None','None','None')
    studentInfo.append({'title': 'University', 'value': data[2]})
    studentInfo.append({'title': 'Thesis Title', 'value': data[3]})
    studentInfo.append({'title': 'Funding Source', 'value': data[4]})
    studentInfo.append({'title': 'Start Date', 'value': data[5], 'id': 'datepicker'})
    studentInfo.append({'title': 'Finish Date (expected)', 'value': data[6], 'id': 'datepicker'})
    studentInfo.append({'title': 'Thesis submission date', 'value': data[7], 'id': 'datepicker'})
    studentInfo.append({'title': 'Student Mentor', 'value': data[8]})
    return studentInfo

@app.route("/")
def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp',methods=['POST'])
def signUp():
    try:
        # read the posted values from the UI
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        # validate the received values
        if _name and _email and _password:
            _hashed_password = generate_password_hash(_password)
            if sp_createUser(_name, _email, _hashed_password):
                return redirect('/')

        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})
    except Exception as e:
            return json.dumps({'error':str(e)})
    finally:
        pass
        # cursor.close()
        # conn.close()

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
        data = sp_validateLogin(_username)
        # print data
        if len(data) > 0:
            if check_password_hash(str(data[0][2]),_password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                # return render_template('error.html',error = 'Wrong Email address or Password.')
                return json.dumps({'error':data[0]})
        else:
            # return render_template('error.html',error = 'Wrong Email address or Password.')
            return json.dumps({'error':data[0]})

    except Exception as e:
        return render_template('error.html',error = str(e))

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/getStudentInfo')
def getStudentInfo():
    try:
        if session.get('user'):
            _user = session.get('user')
            print 'user = ', _user
            info_dict = sp_getStudentInfo(_user)
            return json.dumps(info_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

if __name__ == "__main__":
    app.run()
