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

login_manager = LoginManager()
login_manager.login_view= 'signup'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
	return users.query.get(int(id))

def __init__(self, name, email):
	self.name = name
	self.email = email
@app.route('/view')
def view():
	return render_template("view.html", values=users.query.all())

@app.route('/signup', methods=["POST","GET"])
def signup():
	# If the user is trying to signup....
	if request.method=="POST":
		#Uses the session on line 6
		session.permanent=True
		#gets the firstname name from the form in sign-up.html
		user=request.form["firstname"]
		#Saves the value of user in line 19 into a session with a name value called "user"
		session["user"]=user

		found_user = users.query.filter_by(name=user).first()
		if found_user:
			session["email"]=found_user.email
		else:
			usr=users(user, "")
			db.session.add(usr)
			db.session.commit()
		#Flashes this message after the user has signed up
		flash("You have successfully signed up")
		login_user(found_user,remember=True)
		#Then it redirects them to the /user page
		return redirect(url_for("user"))
	else:
		# If the user is already signed in
		if "user" in session:
			#FLash this message
			flash("You are already logged in!")
			#And redirect them to the /user page 
			return redirect("user")

		return render_template('sign-up.html')

@app.route('/')
@login_required
def home():
	return render_template('index.html', user=current_user)

@app.route('/user', methods=["POST","GET"])
def user():
	email = None
	if "user" in session:
		user = session["user"]
		if request.method=="POST":
			email = request.form["email"]
			session["email"] = email
			found_user = users.query.filter_by(name=user).first()
			found_user.email = email
			db.session.commit()
			flash("Email was saved!")
		else:
			if "email" in session:
				email=session["email"]

		return render_template("user.html", email=email)
	else:
		flash("You are not logged in!")
		return redirect(url_for('signup'))

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash("You have successfully logged out!", "info")
	session.pop("user", None)
	session.pop("email", None)
	return redirect(url_for("signup"))
db.create_all()
app.run(host='0.0.0.0', port=8080, debug=True)