from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

class SignupForm(FlaskForm):
	firstname = StringField("firstname", render_kw={'placeholder': 'firstname'}, validators=[DataRequired()])
	lastname = StringField("lastname", render_kw={'placeholder': 'lastname'}, validators=[DataRequired()])
	username = StringField("username", render_kw={'placeholder': 'username'}, validators=[DataRequired()])
	email = StringField("email", render_kw={'placeholder': 'email'}, validators=[DataRequired()])
	about_author = TextAreaField("About Author")
	password = PasswordField('Password', render_kw={'placeholder': 'Password'}, validators=[DataRequired(), EqualTo('confirm_password', message='Passwords Must Match!')])
	confirm_password = PasswordField('confirm password', render_kw={'placeholder': 'confirm password'}, validators=[DataRequired()])
	profile_pic = FileField("Profile Pic")
	submit = SubmitField("signup")

class LoginForm(FlaskForm):
	email = StringField("email", render_kw={'placeholder': 'email'}, validators=[DataRequired()])
	password = PasswordField('password', render_kw={'placeholder': 'password'}, validators=[DataRequired()])
	submit = SubmitField("login")

class PostForm(FlaskForm):
	username = StringField("username", render_kw={'placeholder': 'username'}, validators=[DataRequired()])
	title = StringField("Title", render_kw={'placeholder': 'title'}, validators=[DataRequired()])
	content = CKEditorField('Content', render_kw={'placeholder': 'start typing here'}, validators=[DataRequired()])
	tag = StringField("Slug", render_kw={'placeholder': 'slug'}, validators=[DataRequired()])
	submit = SubmitField("Submit")

class SearchForm(FlaskForm):
	searchfield = StringField("Search", render_kw={'placeholder': 'search...'}, validators=[DataRequired()])
	submit = SubmitField("Search")

class BlogPostForm(FlaskForm):
	username = StringField("username", render_kw={'placeholder': 'username'}, validators=[DataRequired()])
	title = StringField("Title", render_kw={'placeholder': 'title'}, validators=[DataRequired()])

	def validate_image(form, field):
		if field.data:
			file_size = len(field.data.read())
			max_size = 10 * 1024 * 1024  # 10MB
			if file_size > max_size:
				raise ValidationError('File size must not exceed 10MB.')
    
		image = FileField('Image', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
		])
	content = TextAreaField('Content', render_kw={'placeholder': 'start typing here...'}, validators=[DataRequired()])
    
	submit = SubmitField('Submit')
