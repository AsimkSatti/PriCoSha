#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
from flask import Markup

import time
import datetime

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='pricoshia',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

@app.route('/back')
def back():
	username = session['username']
	return redirect(url_for('home'))

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM person WHERE (username = %s AND pssword = %s)'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	fname = request.form.get("firstname",None)
	lname = request.form.get("lastname", None)
	

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM person WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):

		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO person VALUES(%s, %s,%s, %s)'
		cursor.execute(ins, (username, password,fname,lname))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/notice', methods=['GET', 'POST'])
def notice():
	username = session['username']
	cursor = conn.cursor();
	mgroups = 'SELECT * FROM tag NATURAL JOIN content WHERE tagee=%s AND statse=0'
	cursor.execute(mgroups,(username))
	vuert2=cursor.fetchall()
	conn.commit()
	cursor.close()


	return render_template('notice.html', username=username, tert=vuert2)



@app.route('/decider', methods=['GET', 'POST'])
def decider():
	username = session['username']
	cursor = conn.cursor();

	which=request.form.get("vuo")

	if(request.form.get("sino")):
		ins = 'UPDATE tag SET statse = 1  WHERE tagee=%s AND ID=%s'

		cursor.execute(ins,(username,which))
	else:
		dell='DELETE FROM tag WHERE tagee=%s AND ID=%s'
		cursor.execute(dell,(username,which))

	conn.commit()
	

	cursor.close()
	return redirect(url_for('notice'))



@app.route('/home', methods=['GET', 'POST'])
def home():
	username = session['username']
	cursor = conn.cursor();
	pquery = 'SELECT item_date,name,id FROM content WHERE poster_username = %s ORDER BY item_date DESC;'

	cursor.execute(pquery,(username))

	data = cursor.fetchall()
	cursor.close()

	cursor = conn.cursor();
	ppquery="SELECT * FROM person "


	cursor.execute(ppquery)
	data1=cursor.fetchall()
	cursor.close()


	cursor = conn.cursor();
	noto="SELECT ID FROM tag "


	cursor.execute(noto)
	r=cursor.fetchone()
	cursor.close()
	notoro=str(r)


	cursor = conn.cursor();
	idss="SELECT * FROM tag NATURAL JOIN content NATURAL JOIN person WHERE tagee=username AND statse=1 AND ID=%s "
	cursor.execute(idss, (notoro))
	data2=cursor.fetchall()
	cursor.close()
	return render_template('home.html', username=username, posts=data, people=data1,itchi=data2)


@app.route('/tag', methods=['GET', 'POST'])
def tag():
	i=0
	username = session['username']
	cursor = conn.cursor()
	ts = time.time()
	error=None
	now = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	# result = {"Albumi": []}
	# result == ""
	homie=request.form.get("humn")
	print("/n")
	print(homie)
	tpost=request.form.get("vute")
	print("/n")
	print(tpost)
	if(username==homie):
		inesrtion='INSERT INTO tag VALUES(%s, %s,%s,True,%s)'
		cursor.execute(inesrtion, (username, homie,now, tpost))

	else:
		cursor = conn.cursor()
		noto="SELECT is_pub FROM content WHERE  ID=%s"
		cursor.execute(noto,(tpost))
		r=cursor.fetchone()
		print(r)
		print("/n")
		if(r!={'is_pub': 1}):
			cursor = conn.cursor()
			inesrtion='INSERT INTO tag VALUES(%s, %s,%s,False,%s)'
			cursor.execute(inesrtion, (username, homie,now, tpost))
			conn.commit()
		else:
			return render_template('home.html', error=error)


	cursor.close()
	return redirect(url_for('home'))

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	ts = time.time()
	now = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	username = session['username']
	cursor = conn.cursor()
	blog = request.form['blog']
	query = 'INSERT INTO content(item_date,Name, is_pub, poster_username) VALUES(%s,%s,%s,%s)'

	if(request.form.get("vino")):
		cursor.execute(query, (now,blog,0, username))

	else:
		cursor.execute(query, (now,blog,1, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/makegroup', methods=['GET', 'POST'])
def makegroup():
	username = session['username']
	title= request.form.get("title")
	friend = request.form.get("fuser1")
	cursor = conn.cursor()
	query='SELECT username FROM person WHERE username = %s'
	cursor.execute(query, (friend,))
	data = cursor.fetchone()
	if(data):
		cursor = conn.cursor()
		groupalreadyexist='SELECT name FROM friendgroup WHERE owner_username = %s AND name=%s'
		cursor.execute(groupalreadyexist,(username,title,))
		data1 = cursor.fetchone()
		if(data1 ==None):
			n='INSERT INTO friendgroup(Name, owner_username) VALUES(%s,%s)'
			cursor.execute(n, (title, username))
			p='INSERT INTO member(member,owner,Name) VALUES(%s,%s,%s)'
			cursor.execute(p, (friend, username,title))
	cursor.close()
	return render_template('makegroup.html')


@app.route('/group')
def group():
	username = session['username']
	cursor = conn.cursor();

	
	fgroups = 'SELECT name,member,owner FROM member WHERE member = (SELECT firstname FROM person WHERE username = %s)'

	#whosein = 'SELECT * FROM `member` WHERE owner IN(SELECT `owner` FROM member WHERE `member`=%s) AND Name IN(SELECT name FROM member WHERE `member`=%s) '



	cursor.execute(fgroups,(username))
	#cursor.execute(whosein,(username,username))

 

	peps=cursor.fetchall()


	cursor.close()
	return render_template('group.html', username=username, group=peps)

@app.route('/seegroup')
def seegroup():
	return redirect(url_for('group'))

@app.route('/yournotice')
def yournotice():
	return redirect(url_for('notice'))

@app.route('/creategroup')
def creategroup():
	return redirect(url_for('makegroup'))


@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5090, debug = True)
