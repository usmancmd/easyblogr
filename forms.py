from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

class SignupForm(FlaskForm):
	firstname = StringField("firstname", validators=[DataRequired()])
	lastname = StringField("lastname", validators=[DataRequired()])
	email = StringField("email", validators=[DataRequired()])
	about_author = TextAreaField("About Author")
	password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords Must Match!')])
	confirm_password = PasswordField('confirm password', validators=[DataRequired()])
	profile_pic = FileField("Profile Pic")
	submit = SubmitField("submit")

class LoginForm(FlaskForm):
	email = StringField("enter your email", validators=[DataRequired()])
	password = PasswordField('enter your password', validators=[DataRequired()])
	submit = SubmitField("submit")



