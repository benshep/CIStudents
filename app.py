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

class Column:
    def __init__(self, sql_name, pos=None, length=45, is_date=False, is_unique=False, default_value=None):
        [setattr(self, attr, val) for attr, val in locals().items() if attr != 'self']

    def __str__(self):
        return '`{sql_name}` VARCHAR({length}) NULL'.format(**self.__dict__) + \
               (' UNIQUE' if self.is_unique else '') + \
               ((" DEFAULT '" + self.default_value + "'") if self.default_value else '')

    def __repr__(self):
        return '<Column ' + self.sql_name + '>'

# Column = collections.namedtuple('Column', 'sql_name pos length is_date is_unique')
# Column.__new__.__defaults__ = ('', None, 45, False, False)  # defaults for pos, len, date, unique

username_col = Column('user_name', 0, is_unique=True)
user_columns = collections.OrderedDict([
                ('Name', username_col),
                ('Email Address', Column('user_username', 1)),
                ('Password', Column('user_password'))])
info_columns = collections.OrderedDict([
                ('Name', username_col),
                ('University', Column('University', 1, default_value='None')),
                ('Thesis Title', Column('Thesis_title', 2, length=450, default_value='None')),
                ('Funding Source', Column('Funding_source', 3, length=145, default_value='None')),
                ('Start Date', Column('Start_date', 4, is_date=True, default_value='None')),
                ('Expected Finish Date', Column('Expected_finish_date', 5, is_date=True, default_value='None')),
                ('Supervisor', Column('Supervisor', 6, default_value='None')),
                ('Thesis Submission Date', Column('Thesis_submission_date', 7, is_date=True, default_value='None')),
                ('Student Mentor', Column('Student_mentor', 8, default_value='None'))])
lecture_columns = collections.OrderedDict([
                ('Name', username_col),
                ('Lecture course', Column('Lecture_course', 1)),
                ('Attendance', Column('Attendance', 2)),
                ('Record', Column('Record', 3, length=450))])
skills_columns = collections.OrderedDict([
                ('Name', username_col),
                ('Skill', Column('Skill', 1))])
assessments_columns = collections.OrderedDict([
                ('Name', username_col),
                ('Assessment', Column('Assessment', 1)),
                ('Result', Column('Result', 2))])

try:
    print 'creating user table'
    command = 'CREATE TABLE tbl_user (' + ', '.join([str(col) for col in user_columns.values()]) + ')'
    cursor.execute(command)
except Exception as e:
        print e

try:
    # cursor.execute('''DROP TABLE tbl_info''')
    print 'creating info table'
    command = 'CREATE TABLE tbl_info (' + ', '.join([str(col) for col in info_columns.values()]) + ')'
    cursor.execute(command)
except Exception as e:
        print e

cursor.execute('SELECT * FROM tbl_info')
data = cursor.fetchall()
print data

try:
    print 'creating lectures table'
    command = 'CREATE TABLE tbl_lectures (' + ', '.join([str(col) for col in lecture_columns.values()]) + ')'
    cursor.execute(command)
except Exception as e:
        print e

try:
    print 'creating skills table'
    command = 'CREATE TABLE tbl_skills (' + ', '.join([str(col) for col in skills_columns.values()]) + ')'
    cursor.execute(command)
except Exception as e:
        print e

try:
    print 'creating assessments table'
    command = 'CREATE TABLE tbl_assessments (' + ', '.join([str(col) for col in assessments_columns.values()]) + ')'
    cursor.execute(command)
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
        print k, v
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
