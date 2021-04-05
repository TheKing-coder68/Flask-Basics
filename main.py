from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
from flask_login.mixins import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_manager, login_user, login_required, logout_user, current_user
from flask_login import LoginManager

app = Flask('app')
app.config['SECRET_KEY']='Sometimes life just sucks.'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False

app.permanent_session_lifetime= timedelta(minutes=2)
db = SQLAlchemy(app)

class users(db.Model, UserMixin):
	_id=db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(150))
	email=db.Column(db.String(150))
	def get_id(self):
           return (self._id)

# Assigned the LoginManager() into login_manager
login_manager = LoginManager()
# Reidrect the user to the Signup page if they aren't logged/signed in
login_manager.login_view= 'signup'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
	return users.query.get(int(id))

def __init__(self, name, email):
	self.name = name
	self.email = email
# Shows all of the users and user information so far
@app.route('/view')
def view():
	return render_template("view.html", values=users.query.all())

@app.route('/signup', methods=["POST","GET"])
def signup():
	# If the user is trying to signup....
	if request.method=="POST":
		#Uses the session
		session.permanent=True
		#gets the firstname name from the form in sign-up.html and assigns it the value of user
		user=request.form["firstname"]
		#Saves the value of user in line 19 into a session with a name value called "user"
		session["user"]=user
		# Checks to see if the user is in the database
		found_user = users.query.filter_by(name=user).first()
		# If there is a user, assign the session email to the email in the database 
		if found_user:
			session["email"]=found_user.email
		# Else just keep the email area empty and commit the variable, user and the empty email field, into the database
		else:
			usr=users(user, "")
			db.session.add(usr)
			db.session.commit()
		#Flashes this message after the user has signed up
		flash("You have successfully signed up")
		# Basically assigns the value of found_user to login_user and remembers it so that it can be used later in the program
		login_user(found_user,remember=True)
		#Then it redirects them to the /user page
		return redirect(url_for("user"))
	else:
		# If the user is already signed in
		if "user" in session:
			#Flash this message
			flash("You are already logged in!")
			#And redirect them to the /user page 
			return redirect("user")

		return render_template('sign-up.html')

@app.route('/')
#The homepage requires that the user is logged in, if the user isn't logged in, it should redirect to the signup page
@login_required
# Gives the value user to the current_user which came with the loginmanger package
def home():
	return render_template('index.html', user=current_user)

@app.route('/user', methods=["POST","GET"])
def user():
	# Creates an empty email variable that will later be used
	email = None
	#If user in session...
	if "user" in session:
		#Assigns session user to the variable user
		user = session["user"]
		#If they are adding an email...
		if request.method=="POST":
			#Assigns the email that was submitted in the form to the empty email variable from earlier
			email = request.form["email"]
			#Then makes the email equal to the session email
			session["email"] = email
			# Assigns found_user to the name of the user that is in session
			found_user = users.query.filter_by(name=user).first()
			#Then assigns the user that is in the database, to the email that was entered in the form
			found_user.email = email
			#And commits it into the database
			db.session.commit()
			#And then flashes this message
			flash("Email was saved!")
		else:
			#If the user already saved an email...
			if "email" in session:
				#Assigns the session email to the value of email
				email=session["email"]
			#Passes email into the html 
		return render_template("user.html", email=email)
	else:
		#If not logged in flash the message
		flash("You are not logged in!")
		#Then redirect to the signup page
		return redirect(url_for('signup'))

@app.route('/logout')
#This page requires the user to be logged in
@login_required
def logout():
	#Logs out the user
	logout_user()
	#Then flash this
	flash("You have successfully logged out!", "info")
	#And po the user info and email info
	session.pop("user", None)
	session.pop("email", None)
	#And redirects them to the signup page
	return redirect(url_for("signup"))
	#Creates the db
db.create_all()
app.run(host='0.0.0.0', port=8080, debug=True)