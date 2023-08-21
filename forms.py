from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_wtf.file  import FileField 
from flask_ckeditor import CKEditorField

#Search Form
class SearchForm(FlaskForm):
	searched = StringField("Searched", validators =[DataRequired()])
	submit = SubmitField("Submit")

#Login Form 
class LoginForm(FlaskForm):
	username = StringField("Username", validators =[DataRequired()])
	password = PasswordField("Password", validators =[DataRequired()] )
	submit = SubmitField("Submit")



class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = CKEditorField("Content", validators=[DataRequired()])
	submit = SubmitField("Submit", validators=[DataRequired()])


#Create form class
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("UserName", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	about_author = TextAreaField("About Author", validators=[DataRequired()] )
	profile_pic = FileField("Profile pic")
	password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2',message="Paswwords must match")])
	password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
	submit = SubmitField("Submit")

