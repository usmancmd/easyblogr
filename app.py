from flask import Flask, render_template, flash, request, redirect, url_for, current_app
from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_migrate import Migrate
from datetime import date
from argon2 import PasswordHasher
from werkzeug.security import generate_password_hash, check_password_hash 
from forms import SignupForm, LoginForm, BlogPostForm, SearchForm, PostForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user



from flask_session import Session
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
from dotenv import load_dotenv
from PIL import Image
import base64
import secrets
import os

load_dotenv()
SECRETKEY = os.getenv('SECRETKEY')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
HOSTNAME = os.getenv('HOSTNAME')
DATABASE_NAME = os.getenv('DATABASE_NAME')


app = Flask(__name__)
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)


# Secret Key!
app.config['SECRET_KEY'] = SECRETKEY

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}/{DATABASE_NAME}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db


# Add CKEditor
ckeditor = CKEditor(app)

# Flask_Login configurations
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	from models import Users
	return Users.query.get(int(user_id))


login_manager.init_app(app)


# function to 
def base64_encode(data):
    if data:
        return base64.b64encode(data).decode('utf-8')
    return None

# Register the custom Jinja2 filter
app.jinja_env.filters['b64encode'] = base64_encode

# def verify_password(self, email, password):
#	from models import Users
# 	ph = PasswordHasher()
# 	raw_hash = ph.hash(password)
# 	const = raw_hash[:31]
# 	passwd = Users.query.filter_by(email).value(Users.password)
# 	hashed_pw = const + passwd
# 	return ph.verify(hashed_pw, password)

def get_short_description(content, max_words=25):
    words = content.split()  # Split the content into words
    short_words = words[:max_words]  # Take the first max_words words
    short_description = ' '.join(short_words)  # Join the words back into a string
    return short_description+' ...'

def save_images_blogs(image):
	image_hash = secrets.token_urlsafe(10)
	_, file_extension = os.path.splitext(image.filename)
	image_name = f"{image_hash}{file_extension}"
	file_path = os.path.join(current_app.root_path, 'static/blogs_img', image_name)
	image.save(file_path)
	return image_name

def save_images_profile(image):
	image_hash = secrets.token_urlsafe(10)
	_, file_extension = os.path.splitext(image.filename)
	image_name = f"{image_hash}{file_extension}"
	file_path = os.path.join(current_app.root_path, 'static/profile_img', image_name)
	image.save(file_path)
	return image_name

@app.route('/')
def index():
    return render_template('index.html')


# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	from models import Users
	form = SignupForm()
	# if form.validate_on_submit():
	if request.method == 'POST':
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			# ph = PasswordHasher()
			# raw_hash = ph.hash(form.password.data)
			# sorted_hash = raw_hash[31:97]
			hashed_pw = generate_password_hash(form.password.data, "sha256")
			fullname = f'{form.firstname.data} {form.lastname.data}'
			user = Users(fullname=fullname, email=form.email.data, password_hash=hashed_pw)
			try:
				db.session.add(user)
				db.session.commit()
			except Exception as e:
	 			return f'{e}'
		form.firstname.data = ''
		form.lastname.data = ''
		form.email.data = ''
		form.password.data = ''

		flash("Thank you for signing up, login!")
		# login_user(user)
		return	redirect(url_for('login'))
	return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    from models import Users
    form = LoginForm()
    
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successful")
                # render_template('blogs.html')
                return redirect(url_for('blogs'))
            else:
                flash("Invalid credentials-p")
        else:
            flash("Invalid credentials")
            
    return render_template('login.html', form=form)




# @app.route('/login', methods=['GET', 'POST'])
# def login():
# 	from models import Users
# 	form = LoginForm(request.form)
# 	if form.validate_on_submit():
# 		email = Users.query.filter_by(email=form.email.data).first()
# 		if email:
# 			pw_hash = Users.query.filter_by(email=form.email.data).value(Users.password_hash)
# 			if check_password_hash(pw_hash, form.password.data):
# 				login_user(email)
# 				# session["email"] = email
# 				# flash("login successfull")
# 				return redirect(url_for('blogs'))
# 			else:
# 				flash("Wrong Password - Try Again!")
# 		else:
# 			flash("User Doesn't Exist!")

# 	return render_template('login.html', form=form,)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html')


# @app.route('/nav')
# def nav():
# 	# search = SearchForm()
# 	return render_template('navbar1.html')


@app.route('/blogs')
def blogs():
	from models import Users, Posts
	search = SearchForm()
	# posts = Posts.query.order_by(desc(Posts.date_posted)).all()
	posts = Posts.query.order_by(Posts.date_posted.desc()).all()


	return render_template('blogs.html',
							search=search,
							posts=posts)

@app.route('/blogs/<int:id>')
def read_more(id):
	post = Posts.query.get_or_404(id)
	return render_template('read_more.html', post=post)


@app.route('/profile')
@login_required
def profile():
	fullname = current_user.fullname
	name = fullname.split()[0]
	return render_template('profile.html', name=name)


@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create():
	from models import Posts
	form = BlogPostForm()
	if form.validate_on_submit():
		title = form.title.data
		image = save_images_blogs(form.image.data)
		description = get_short_description(form.content.data)
		content = form.content.data

		post = Posts(title=title, image=image, description=description, content=content, author=current_user.fullname, author_id=current_user.id)
		try:
			db.session.add(post)
			db.session.commit()
		except Exception as e:
			return f'{e}'
		finally:
			db.session.close()
		return redirect(url_for('blogs'))
		# return render_template('blogs.html')
	return render_template('create-post.html', form=form)



if __name__ == "__main__":
    app.run(debug=True, port=5001)