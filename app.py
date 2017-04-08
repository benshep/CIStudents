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

Column = collections.namedtuple('Column', 'sql_name pos length is_date is_unique')
Column.__new__.__defaults__ = ('', None, 45, False, False)  # defaults for pos, len, date, unique
username_col = Column('user_name', 0, is_unique=True)
user_columns = collections.OrderedDict([
                ('Name', username_col),
                ('Email Address', Column('user_username', 1)),
                ('Password', Column('user_password'))])
info_columns = collections.OrderedDict([
                ('Name', username_col),
                ('University', Column('University',1)),
                ('Thesis Title', Column('Thesis_title', 2, length=450)),
                ('Funding Source', Column('Funding_source', 3, length=145)),
                ('Start Date', Column('Start_date', 4, is_date=True)),
                ('Expected Finish Date', Column('Expected_finish_date', 5, is_date=True)),
                ('Supervisor', Column('Supervisor', 6)),
                ('Thesis Submission Date', Column('Thesis_submission_date', 7, is_date=True)),
                ('Student Mentor', Column('Student_mentor', 8))])

try:
    print 'creating user table'
    cursor.execute('''CREATE TABLE tbl_user
             (`user_name` VARCHAR(45) NULL UNIQUE,
             `user_username` VARCHAR(45) NULL,
             `user_password` VARCHAR(45) NULL)''')
except Exception as e:
        print e

try:
    # cursor.execute('''DROP TABLE tbl_info''')
    print 'creating info table'
    cursor.execute('''CREATE TABLE tbl_info
             (`user_name` VARCHAR(45) UNIQUE NULL,
             `University` VARCHAR(45) DEFAULT 'None',
             `Thesis_title` VARCHAR(450)  DEFAULT 'None',
             `Funding_source` VARCHAR(145)  DEFAULT 'None',
             `Start_date` VARCHAR(45)  DEFAULT 'None',
             `Expected_finish_date` VARCHAR(45)  DEFAULT 'None',
             `Supervisor` VARCHAR(45)  DEFAULT 'None',
             `Thesis_submission_date` VARCHAR(45)  DEFAULT 'None',
             `Student_mentor` VARCHAR(45)  DEFAULT 'None')''')
except Exception as e:
        print e

cursor.execute('SELECT * FROM tbl_info')
data = cursor.fetchall()
print data

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
        # print 't = ', t
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
    # print data
    studentInfo = list()
    for k, v in user_columns.iteritems():
        if not v[1] == None:
            si = {'title': k, 'value': data[v[1]]}
            if v[3]:
                si['class'] = 'datepicker'
            studentInfo.append(si)
    cursor.execute('SELECT * FROM tbl_info WHERE user_name = ?', t)
    data = cursor.fetchone()
    if data == None:
        data = ('None','None','None','None','None','None','None','None','None')
    for k, v in info_columns.iteritems():
        if not k == 'Name' and not v[1] == None:
            si = {'title': k, 'value': data[v[1]]}
            if v[3]:
                si['class'] = 'datepicker'
            studentInfo.append(si)
    return studentInfo

@app.route('/postStudentInfo', methods=['POST'])
def sp_setStudentInfo():
    # which table to update?
    col_name = request.form['name']
    tbl_name = 'tbl_user' if col_name in ('Name', 'Email Address') else 'tbl_info'
    if tbl_name == 'tbl_user':
        sql_column = user_columns[request.form['name']][0]
    else:
        sql_column = info_columns[request.form['name']][0]
    cursor.execute('INSERT OR IGNORE INTO '+tbl_name+' (user_name, '+sql_column+') VALUES(\''+request.form['pk']+'\', \''+request.form['value']+'\')')
    cursor.execute('UPDATE '+tbl_name+' SET '+sql_column+' = \''+request.form['value']+'\' WHERE user_name = \''+request.form['pk']+'\'')
    conn.commit()
    cursor.execute('SELECT * FROM tbl_info')
    data = cursor.fetchall()
    return ''  # send back blank page with response code 200

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
            info_dict = sp_getStudentInfo(_user)
            return json.dumps(info_dict)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

if __name__ == "__main__":
    app.run()
