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
app.config['MYSQL_DATABASE_PASSWORD'] = '*PASSWORD*'
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

@app.route('/viewSinglePhoto/<int:photo_id>', methods=['GET','POST'])
def viewSinglePhoto(photo_id):

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

	# user entered a comment
	if flask.request.method == 'POST':

		if flask_login.current_user.is_authenticated:
			user_id = getUserIdFromEmail(flask_login.current_user.id)
		else:
			user_id = getUnregisteredUserId()

		cursor = conn.cursor()
		cursor.execute(
			'''
				SELECT user_id
				FROM Photos
				WHERE photo_id = {}
			'''.format(photo_id)
		)
		photo_user_id = cursor.fetchone()[0]

		if photo_user_id != user_id:
			cursor = conn.cursor()
			cursor.execute(
				'''
					INSERT
					INTO Comments(user_id, photo_id, text, date)
					VALUES ('{0}', '{1}', "{2}", CURRENT_DATE())
				'''.format(user_id, photo_id, flask.request.form['content'])
			)
		else:
			return 'You cannot comment on your own photo'

	# getting comments
	cursor = conn.cursor()
	cursor.execute(
		'''
		SELECT U.first_name, U.last_name, C.text
		FROM Users U, Comments C
		WHERE U.user_id = C.user_id AND C.photo_id = '{0}'
		'''.format(photo_id)
	)
	comment_data = cursor.fetchall()
	comments = []
	for row in comment_data:
		name = '{} {}'.format(row[0], row[1])
		comment = row[2]
		comments.append([name, comment])

	return render_template(
		'viewSinglePhoto.html',
		caption=photo_data[0],
		photo=photo_data[1],
		base64=base64,
		n_likes=n_likes, 
		user_str=user_str,
		comments=comments,
		photo_id=photo_id
	)

@app.route('/like/<int:photo_id>')
@flask_login.login_required
def like_action(photo_id):

	print(photo_id)

	if flask_login.current_user.is_authenticated:
		user_id = getUserIdFromEmail(flask_login.current_user.id)
	else:
		return 'You must log in before you like a photo'

	print(user_id)

	cursor = conn.cursor()
	cursor.execute(
		'''
			INSERT 
			INTO Likes(photo_id,user_id)
			VALUES ('{0}', '{0}')
		'''.format(photo_id, user_id)
	)
	conn.commit()
	
	return redirect(request.referrer)

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


def getUserId():
	if flask_login.current_user.is_authenticated:
		user_id = getUserIdFromEmail(flask_login.current_user.id)
	else:
		user_id = getUnregisteredUserId()
	return user_id

@app.route('/logout')
def logout():
	flask_login.logout_user()
	photos = getAllPhotos()
	user_id = getUserId()
	return render_template('hello.html', message='Logged out' , photos = photos, base64=base64, user_id = user_id)

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')



@app.route("/register", methods=['POST'])
def register_user():
	try:
		lastname = request.form.get('lastname')
		firstname = request.form.get('firstname')
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		(cursor.execute("INSERT INTO Users (email, first_name, last_name, password) VALUES ('{0}', '{1}' , '{2}' , '{3}')".format(email,firstname, lastname, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=firstname, message='Account Created!')
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

def getYOURPhotosbyComments(comment):
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Photos, Comments WHERE Comments.text = '{0}' AND Photos.photo_id = Comments.photo_id AND Photos.user_id = '{1}'".format(comment, user_id))
	return cursor.fetchall()

def getPhotosbyTags(tags):
	tag = tags.split()
	arr = []
	print("checkpoint1")
	for x in tag:
		dict = {}
		tag_id = getTagId(x)
		# print(x, tag_id)
		cursor = conn.cursor()
		cursor.execute("SELECT Photos.* FROM Tagged, Photos WHERE tag_id = '{0}' AND Tagged.photo_id = Photos.photo_id".format(tag_id))
		temp = cursor.fetchall()
		for i in temp:
			dict[i[0]] = i
		arr.append(dict)
	final = []
	print("checkpoint2")
	for key in arr[0]:
		boolean = True
		for x in arr:
			if key not in x:
				boolean = False
		if boolean:
			final.append(arr[0][key])
	print(len(final))
	return final

def getAlbumNameFromAlbumId(id):
	cursor = conn.cursor()
	cursor.execute("SELECT name FROM Albums WHERE albums_id = '{0}'".format(id))
	return cursor.fetchone()[0]

def getYOURPhotosbyTags(tags):
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	tag = tags.split()
	arr = []
	print("checkpoint1")
	for x in tag:
		dict = {}
		tag_id = getTagId(x)
		# print(x, tag_id)
		cursor = conn.cursor()
		cursor.execute("SELECT Photos.* FROM Tagged, Photos WHERE tag_id = '{0}' AND Tagged.photo_id = Photos.photo_id AND Photos.user_id = '{1}'".format(tag_id , user_id))
		temp = cursor.fetchall()
		for i in temp:
			dict[i[0]] = i
		arr.append(dict)
	final = []
	print("checkpoint2")
	for key in arr[0]:
		boolean = True
		for x in arr:
			if key not in x:
				boolean = False
		if boolean:
			final.append(arr[0][key])
	print(len(final))
	return final

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
	return cursor.fetchone()[0]

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

def getTagId(name):
	cursor = conn.cursor()
	cursor.execute("SELECT tag_id FROM Tags WHERE name = '{0}'".format(name))
	return cursor.fetchone()[0]

def getAllAlbums():
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM ALbums")
	return cursor.fetchall()


def getLeaderboard():
	cursor = conn.cursor()
	cursor.execute(
		'''
		SELECT user_id, first_name, last_name
		FROM Users
		'''
	)
	user_data = cursor.fetchall()
	user_ids = [row[0] for row in user_data]
	user_names = ['{} {}'.format(row[1], row[2]) for row in user_data]

	cursor = conn.cursor()
	cursor.execute('''
		SELECT COUNT(*), user_id
		FROM Photos 
		GROUP BY user_id
		''')
	# print(cursor.fetchall())
	photos = cursor.fetchall()

	cursor = conn.cursor()
	cursor.execute('''
		SELECT COUNT(*), user_id 
		FROM Comments 
		GROUP BY user_id
		''')
	comments = cursor.fetchall()

	score_dict = {}
	name_dict = {}
	for i, user_id in enumerate(user_ids):
		score_dict[user_id] = 0
		name_dict[user_id] = user_names[i]

	for x in photos:
		score_dict[x[1]] = x[0]
	
	for x in comments:
		score_dict[x[1]] += x[0]

	leaders_ids_scores = []
	for key in score_dict.keys():
		leaders_ids_scores.append([key, score_dict[key], name_dict[key]])
	
	leaders_ids_scores.sort(key = lambda x: x[1])
	leaders_ids_scores.reverse()

	leaders_names = [row[2] for row in leaders_ids_scores]
	leaders_scores = [row[1] for row in leaders_ids_scores]

	if len(leaders_names) < 10: 
		return leaders_names, leaders_scores
	else: 
		return leaders_names[-10:], leaders_scores[-10:]

def getName(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchone()

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

		

def isPhotoCaptionUnique(name):
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	if cursor.execute("SELECT name  FROM Photos WHERE name = '{0}' AND user_id = '{1}'".format(name, user_id)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True


def isAlbumReal(name):
	cursor = conn.cursor()
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if cursor.execute("SELECT name FROM Albums WHERE name = '{0}' AND user_id = '{1}'".format(name, user_id)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

#end login code
def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Photos")
	return cursor.fetchall()

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
	return redirect(url_for('hello', name=flask_login.current_user.id, message="Here's your profile"))

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]




@app.route('/upload/<int:albums_id>', methods=['GET', 'POST'])
@flask_login.login_required
def upload(albums_id):
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	if request.method == 'POST':
		imgfile = request.files['photo']
		caption = request.form['caption']
		photo_data = imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''
			INSERT INTO 
			Photos (caption, data, albums_id, user_id) 
			VALUES ( %s, %s, %s, %s )
		''' ,(caption, photo_data, albums_id, user_id))
		conn.commit()
		cursor = conn.cursor()
		cursor.execute("SELECT LAST_INSERT_ID()")
		photo_id = cursor.fetchone()
		tags = request.form['tags'].split()
		for x in tags:
			cursor = conn.cursor()
			print(cursor.execute('''SELECT name FROM Tags WHERE name = %s''', (x)) )
			if cursor.execute('''SELECT name FROM Tags WHERE name = %s''', (x)) == 0: #tag not in table yet
				print("test")
				cursor = conn.cursor()
				cursor.execute('''INSERT INTO Tags (name) VALUES (%s)''',(x))
				conn.commit()
			tag_id = getTagId(x)
			cursor.execute('''INSERT INTO Tagged (photo_id, tag_id) VALUES (%s, %s)''',(photo_id, tag_id))
			conn.commit()
		return redirect(url_for('profileOverview'))
	else:
		cursor = conn.cursor()
		if cursor.execute("SELECT * FROM Albums WHERE user_id = '{0}'".format(user_id)) == 0:
			return redirect(url_for('profileOverview', error = "Must Create Album before uploading photos")) 
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


@app.route("/viewAlbum/<int:albums_id>" , methods=['GET', 'POST'])
# @flask_login.login_required
def viewAlbum(albums_id):
	primaryuser = False
	user_id = getUserId()
	if request.method == 'POST':
		if request.form['action'] == "delete":
			photo_id = request.form['photo']
			deletePhotos(photo_id)
		
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM ALbums WHERE albums_id = '{0}'".format(albums_id))
	albumCreator = cursor.fetchone()[0]
	print(albumCreator, user_id)
	if albumCreator == user_id:
		primaryuser = True
		
	return render_template(
		'viewAlbum.html', 
		album = getAlbumPhotos(albums_id), 
		base64=base64, 
		albums_id = albums_id, 
		album_name=getAlbumNameFromAlbumId(albums_id),
		primaryuser = primaryuser
	)


@app.route("/", methods=[ "POST"])
def searchfunction():
	user_id = getUserId()
	if request.form['action'] == "photosearch":
		if request.form['searchTypeButton'] == "Search All Photos By Tags":
			tags = request.form['text']
			photos = getPhotosbyTags(tags)
			return render_template('hello.html', photos=photos , base64=base64, user_id=user_id)

		elif request.form['searchTypeButton'] == "Search All Photos By Comments":
			comments = request.form['comments']
			photos = getPhotosbyComments(comments)
			return render_template('hello.html', photos = photos , base64=base64,  user_id=user_id )

		elif request.form['searchTypeButton'] == "Search Your Photos By Comments":
			comments = request.form['comments']
			photos = getYOURPhotosbyComments(comments)
			return render_template('hello.html', photos = photos , base64=base64,  user_id=user_id)

		elif request.form['searchTypeButton'] == "Search Your Photos By Tags":
			tags = request.form['text']
			photos = getYOURPhotosbyTags(tags)
			return render_template('hello.html', photos=photos , base64=base64,  user_id=user_id)

	if request.form['action'] == "showAlbums":
			albums = getAllAlbums()
			return render_template('hello.html', albums= albums,  user_id=user_id)
	else:
		photos = getAllPhotos()
		return render_template('hello.html', message='Welecome to Photoshare',photos = getAllPhotos(), base64=base64 , user_id=user_id) 

#default page
@app.route("/")
def hello():
	user_id = getUserId()
	leaders, leaders_scores = getLeaderboard()
	return render_template(
		'hello.html', 
		message='Welecome to Photoshare' , 
		photos = getAllPhotos(), 
		base64=base64,
		user_id=user_id, 
		leaders = leaders,
		leaders_scores = leaders_scores,
		len_leaders = len(leaders)
	) 
	#get list of photos

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
