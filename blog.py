from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from forms import UserForm, LoginForm, PostForm, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_login import  UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_ckeditor import CKEditor
import uuid as uuid
import os

# Create Flask instance
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12A1339%40a@localhost/users'

#Secret Key
app.config['SECRET_KEY'] = "anu"

#Initialize DB
db = SQLAlchemy(app) 
migrate = Migrate(app,db)
ckeditor = CKEditor(app)

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

with app.app_context():
    db.create_all()

# flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

#Pass to Navbar -- passes to base file
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # Get data from submitted form
        searched = form.searched.data
        # Query the Database
        posts = Posts.query.filter(Posts.title.like('%' + searched + '%')).order_by(Posts.title)
        return render_template("search.html",
            form=form,
            searched=searched,
            posts=posts)



@app.route('/')
def index():
	return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"),404

@app.route('/register',methods=['GET','POST'])
def register ():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			#Hashing pswd
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(username=form.username.data,name=form.name.data,about_author=form.about_author.data, email=form.email.data, password_hash=hashed_pw,profile_pic=form.profile_pic.data) 
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.about_author.data=''
		form.password_hash.data = ''
		form.profile_pic.data = ''

		flash("User Added Successfully")
		return redirect(url_for('login'))
	our_users = Users.query.order_by(Users.date_added)
	return render_template("register.html", 
		form = form,
		name = name,
		our_users=our_users )

##LOGIN PAGE
@app.route('/login',methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username = form.username.data).first()
		if user:
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login successful")
				return redirect(url_for('posts'))
			else:
				flash("Incorrect Password")
		else:
				flash("User doesn't exist")

	return render_template('login.html',form = form)


@app.route('/profile', endpoint='profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/update/<int:id>',methods=['GET','POST'])
@login_required
def update(id):
	form = UserForm()
	id = current_user.id
	to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		to_update.name = request.form['name']
		to_update.username = request.form['username']
		to_update.email = request.form['email']
		to_update.about_author = request.form['about_author']
		to_update.profile_pic = request.files ['profile_pic']

	# Check for profile pic
		if request.files['profile_pic']:
			to_update.profile_pic = request.files['profile_pic']

			# Grab Image Name
			pic_filename = secure_filename(to_update.profile_pic.filename)
			# Set UUID
			pic_name = str(uuid.uuid1()) + "_" + pic_filename
			# Save That Image
			saver = request.files['profile_pic']
			
			# Change it to a string to save to db 
			to_update.profile_pic = pic_name
			try:
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
				flash("User Updated Successfully!")
				return render_template("profile.html", 
					form=form,
					to_update = to_update)
			except:
				flash("Error!  Looks like there was a problem...try again!")
				return render_template("update.html", 
					form=form,
					to_update = to_update)
		else:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("profile.html", 
				form=form, 
				to_update = name_to_update)
	else:
		return render_template("update.html", 
				form=form,
				to_update = to_update,
				id = id)

	return render_template('update.html')	

## Log Out
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
	logout_user()
	flash("Logged Out")
	return redirect(url_for('login'))

@app.route('/posts')
@login_required
def posts():
	post = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", post=post)

@app.route('/posts/<int:id>')
@login_required
def view_post(id):
	post = Posts.query.get_or_404(id)
	return render_template('view_post.html',post=post)


#Add Post page
@app.route('/add-post',methods=['GET','POST'])
@login_required
def add_post():
	form = PostForm()
	if form.validate_on_submit():
		poster = current_user.id
		post = Posts(poster_id = poster, title=form.title.data,content=form.content.data)
		form.title.data = ''
		form.content.data = ''
		

		db.session.add(post)
		db.session.commit()

		flash("Blog post Submitted")
		return redirect(url_for('posts'))



	return render_template("add_post.html",form = form)

@app.route('/posts/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data

		db.session.add(post)
		db.session.commit()

		flash("Post has been Updated")

		return redirect(url_for('view_post',id=post.id))

	if current_user.id == post.poster.id:

		form.title.data = post.title
		form.content.data = post.content
		return render_template('edit_post.html',
			form=form)
	else:
		flash("Cannot Edit")
		post = Posts.query.get_or_404(id)
		return render_template('posts.html',
	   		post=post)


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	id = current_user.id
	post_delete = Posts.query.get_or_404(id)
	if id == post_delete.poster.id or id == 7:
		try:
			db.session.delete(post_delete)
			db.session.commit()

			flash("Post deleted Successfully")

			post = Posts.query.order_by(Posts.date_posted)

			return render_template("posts.html", post=post)

		except:
			flash("Error in Deleting the Post")

			post = Posts.query.order_by(Posts.date_posted)

			return render_template("posts.html", post=post)




	#Create Model
class Users(db.Model,UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), nullable=False, unique=True)
	name = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	about_author = db.Column(db.Text(500), nullable=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	profile_pic = db.Column(db.String(255), nullable=True)

	## PASSSWORD
	password_hash = db.Column(db.String(128))
	#Users can have many posts
	posts = db.relationship('Posts', backref='poster')

	@property
	def password(self):
		raise AttributeError('Password is not a readable attribute')

	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash, password)

	#Create String
	def __repr__(self):
		return '<Name %r>' % self.name

# Create a Blog Post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(255))
	content = db.Column(db.Text)
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	#Foreign key
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
