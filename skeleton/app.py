######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for, session
from flaskext.mysql import MySQL
import flask_login
import datetime as date;

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'SR24mesjw!'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUnregisteredUserId():
	return -1

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/viewSinglePhoto', methods=['GET','POST'])
def viewSinglePhoto():

	photo_id = request.args.get('photo_id', None)

	# get photo data and likes for the page
	cursor = conn.cursor()
	cursor.execute(
		'''
		SELECT caption, data
		FROM Photos
		WHERE Photos.photo_id = {}
		'''.format(photo_id)
	)
	photo_data = cursor.fetchone()
	photo_data = base64.b64encode(photo_data).decode("ascii")

	# getting comments
	cursor = conn.cursor()
	cursor.execute(
		'''
		SELECT C.text
		FROM Users U, Comments C
		WHERE U.user_id = C.user_id AND C.photo_id = {}
		'''.format(photo_id)
	)
	comments = cursor.fetchall()

	# getting number of likes
	cursor.execute(
		'''
		SELECT COUNT(*)
		FROM Likes
		WHERE Likes.photo_id = {}
		'''.format(photo_id)
	)
	n_likes = int(cursor.fetchone()[0])

	# getting users who liked
	cursor.execute(
		'''
		SELECT U.first_name, U.last_name
		FROM Users U, Likes L
		WHERE U.user_id = L.user_id
		'''
	)
	user_list = cursor.fetchall()
	names = ['{} {}'.format(name[0], name[1]) for name in user_list]
	user_str = ', '.join(names)

	# user likes a page
	if flask.request.method == 'POST':

		if flask_login.current_user.is_authenticated:
			user_id = getUserIdFromEmail(flask_login.current_user.id)
		else:
			user_id = getUnregisteredUserId()

		if flask.request.form['like']:
			cursor = conn.cursor()
			cursor.execute(
				'''
					INSERT 
					INTO Likes(photo_id,user_id)
					VALUES ({}, {})
				'''.format(photo_id, user_id)
			)
			conn.commit()
		else:
			cursor = conn.cursor()
			cursor.execute(
				'''
					INSERT
					INTO Comments(user_id, photo_id, text, date)
					VALUES ({}, {}, {}, CURRENT_DATE())
				'''.format(user_id, photo_id, flask.requests.form['text'])
			)

	return render_template(
		'viewSinglePhoto.html',
		caption=photo_data[0],
		photo=photo_data[1], 
		n_likes=n_likes, 
		user_str=user_str,
		comments=comments
	)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
		   <a href='/albumOverview'>Your Alblums</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')


@app.route("/showphotosByTags", methods=['GET', 'POST'])
def showphotos():
	if(request.method == 'POST'):
		if request.form['searchTypeButton'] == 'Search By Tags':
			#get photos by tag value
			return render_template('hello.html', photos="PLACEHOLDER")
		elif request.form['searchTypeButton'] == 'Search By Comments':
			#get photos by comments
			return render_template('hello.html', photos="PLACEHOLDER")



@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password) VALUES ('{0}', '{1}')".format(email, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))


def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Albums WHERE user_id ='{0}'".format(uid))
	return cursor.fetchall()

def getPhoto_id(caption):
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Photos WHERE caption = '{0}' AND user_id = '{1}'".format(caption, user_id))
	return cursor.fetchone()[0]

def getPhotosbyComments(comment):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Photos, Comments WHERE Comments.text = '{0}' AND Photos.photo_id = Comments.photo_id".format(comment))
	return cursor.fetchall()

def getPhotosbyTags(tags):
	tag = tags.split()
	arr = []
	for x in tag:
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Photos, Tags WHERE Tags.name = '{0}' AND Photos.photo_id = Comments.photo_id".format(tags))
		arr.append(cursor.fetchall())


def getAlbumPhotos(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Photos WHERE albums_id = '{0}'".format(album_id))
	return cursor.fetchall()

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getAlbum_IdFromName(name):
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT albums_id FROM Albums WHERE user_id = %s AND name = %s",(user_id, name))
	return cursor.fetchone()#[0]

def deleteAlbum(albumName):
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	album_id = getAlbum_IdFromName(albumName)
	print(album_id)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Tagged T WHERE (SELECT photo_id FROM Photos P WHERE user_id = '{0}' AND P.photo_id = T.photo_id)".format(user_id))
	conn.commit()
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photos WHERE albums_id = '{0}'".format(album_id))
	conn.commit()

	cursor = conn.cursor()
	cursor.execute("DELETE FROM Albums WHERE albums_id = '{0}'".format(album_id))
	conn.commit()


def deletePhoto(data , caption):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id FROM Photos WHERE data = %s AND caption = %s", (data, caption))
	photo_id = cursor.fetchone()
	cursor = conn.cursor()
	cursor.execute('''DELETE FROM Tagged WHERE photo_id = %s''', (photo_id))
	conn.commit()
	cursor.execute('''DELETE FROM Photos WHERE photo_id = %s''', (photo_id))
	conn.commit()


def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True


def isAlbumReal(album_id):
	cursor = conn.cursor()
	if cursor.execute("SELECT name FROM Albums WHERE albums_id = '{0}'".format(album_id)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

#end login code

def deletePhotos(photo_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Tagged WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Photos WHERE photo_id = '{0}'".format(photo_id))
	conn.commit()

@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload():
	print("help")
	if request.method == 'POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form['caption']
		albumName = request.form['albumName']
		album_id = getAlbum_IdFromName(albumName)
		photo_data = imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Photos (caption, data, albums_id, user_id) VALUES ( %s, %s, %s, %s )''' ,(caption, photo_data, album_id, user_id))
		conn.commit()
		photo_id = getPhotosbyComments(caption)
		tags = request.form['tags'].split()
		userPhotos = getUsersPhotos(user_id)
		return redirect(url_for('profileOverview' , photos = userPhotos, base64 = base64, )
	else:	
		return render_template('upload.html')
#end photo uploading code



@app.route('/profileOverview', methods=['GET', 'POST'])
@flask_login.login_required
def profileOverview():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		if request.form['action'] == 'showPhotos':
			return render_template('profileOverview.html', photos = getUsersPhotos(user_id),base64=base64  )
		elif request.form['action'] == 'showAlbums':
			albums = getUsersAlbums(user_id)
			return render_template('profileOverview.html', albums = albums , base64=base64 )

		elif request.form['action'] == 'deleteAlbum':
			user_id = getUserIdFromEmail(flask_login.current_user.id)
			albumName = request.form['albumName']
			deleteAlbum(albumName)
			return render_template('profileOverview.html', albums = getUsersAlbums(user_id), base64=base64 )

		elif request.form['action'] == 'deletePhoto':
			photo_id = request.form['photo_id']
			deletePhotos(photo_id)
			return render_template('profileOverview.html', photos = getUsersPhotos(user_id),base64=base64  )
	else:	
		return render_template('profileOverview.html', albums = getUsersAlbums(user_id), base64=base64 )

@app.route('/createAlbum', methods=['GET', 'POST'])
@flask_login.login_required
def createAlbum():
	if request.method == 'POST':
		#set logice to see if name is already in the database
		Cdate = date.datetime.now()
		name = request.form['title']
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Albums ( name, date ,user_id) VALUES ( %s, %s, %s)''', ( name, Cdate , user_id))
		conn.commit()
		return redirect(url_for('profileOverview', albums = getUsersAlbums(user_id)))
	else:
		return render_template('createAlbum.html')
		#create new album id 


#<albumName> add when I can figure out how to pass it with render_template
@app.route("/viewAlbum" , methods=['POST'])
@flask_login.login_required
def viewAlbum():
	album_id = getAlbum_IdFromName(request.form['albumName'])
	if request.method == 'POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		if request.form['action'] == "delete":
			photo_id = request.form['photo']
			deletePhotos(photo_id)
			return render_template('viewAlbum.html', album = getAlbumPhotos(album_id), base64=base64, album_id = album_id)
		elif request.form['action'] == 'upload':
			imgfile = request.files['photo']
			caption = request.form.get('caption')
			photo_data =imgfile.read()
			cursor.execute('''INSERT INTO Photos ( caption, data, albums_id, user_id) VALUES ( %s, %s, %s, %s )''' ,( caption, photo_data, album_id, user_id))
			conn.commit()
			# tags = request.form['tags'].split()
			# for x in tags:
			# 	cursor = conn.cursor()
			# 	# if cursor.execute('''SELECT tag_id FROM Tags WHERE tag_id = %s''', (tag_id)) == 0:
			# 	cursor.execute('''INSERT INTO Tags (tag_id, name) VALUES (%s)''',( x))
			# 	conn.commit()
			# 	cursor.execute('''INSERT INTO Tagged (photo_id, tag_id) VALUE (%s, %s)''',(photo_id, tag_id))
			# 	conn.commit()
			return render_template('viewAlbum.html', album = getAlbumPhotos(album_id), base64=base64, album_id = album_id) #	else:
		else:
			# album_id = getAlbum_IdFromName(albumName)
			return render_template('viewAlbum.html',  album = getAlbumPhotos(album_id), base64=base64, album_id = album_id )
	else:
		# album_id = getAlbum_IdFromName(albumName)
		return	render_template('viewAlbum.html',  album = getAlbumPhotos(album_id), base64=base64, album_id = album_id )


@app.route('/viewAlbum', methods=['GET'])
@flask_login.login_required
def viewAlbumGet():
	args = request.args
	album_id = getAlbum_IdFromName(args.get("albumName"))
	return	render_template('viewAlbum.html',  album = getAlbumPhotos(album_id), base64=base64, album_id = album_id )


#default page
@app.route("/", methods=['GET'])
def hello():
	if request.form['action'] == "photosearch":
		if request.form['searchTypeButton'] == "Search By Tags":
				
			
			return render_template('hello.html', photos = getPhotosbyTags(request.form['text']), base64 = base64) 
		elif request.form['searchTypeButton'] == "Search By Comments":
			
			return render_template('hello.html', photos = getPhotosbyComments(request.form["text"]), base64 = base64 ) 

	else:	
		return render_template('hello.html', message='Welecome to Photoshare') 
	#get list of photos

def nametoChar(name):
	char = 0
	for x in name:
		char += ord(x)
	return char

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
