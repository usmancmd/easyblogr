from flask import Flask, render_template, flash, request, redirect, url_for, current_app
from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_migrate import Migrate
from datetime import date
from argon2 import PasswordHasher
from werkzeug.security import generate_password_hash, check_password_hash 
from forms import SignupForm, LoginForm, ProfileForm, BlogPostForm, SearchForm, PostForm, CommentForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from dotenv import load_dotenv
import secrets
import os

# initialize flask app
app = Flask(__name__)

# load secret key from hidden .env file
load_dotenv()
SECRETKEY = os.getenv('SECRETKEY')

# set the secret Key!
app.config['SECRET_KEY'] = SECRETKEY

# configure the database uri
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs_sqlite.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

# Add CKEditor 
ckeditor = CKEditor(app)

# Flask_Login configurations
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	"""
	Get user object from the database

	Parameter:
		- user_id: (int) ID of the user

	Returns:
		-  User object with the corresponding user_id
	"""
	from models_sqlite import Users
	return Users.query.get(int(user_id))

login_manager.init_app(app)


def get_short_description(content, max_words=20):
	"""
	Generate short description for blog post

	Parameters:
		- content: (str) blog post content to get short description from
		- max_words: (str) maximum word for the description

	Returns:
		- Short description for post passed as argument
	"""
    words = content.split()  # Split the content into words
    short_words = words[:max_words]  # Take the first max_words words
    short_description = ' '.join(short_words)  # Join the words back into a string
    return short_description+' ...'

# def save_blogs_image(image):
# 	"""save blog post image to the file system in blogs_img directory"""
# 	image_hash = secrets.token_urlsafe(10)
# 	_, file_extension = os.path.splitext(image.filename)
# 	image_name = f"{image_hash}{file_extension}"
# 	file_path = os.path.join(current_app.root_path, 'static/blogs_img', image_name)
# 	image.save(file_path)
# 	return image_name

# def save_profile_image(image):
# 	"""save profile image to the file system in profile_img directory"""
# 	image_hash = secrets.token_urlsafe(10)
# 	_, file_extension = os.path.splitext(image.filename)
# 	image_name = f"{image_hash}{file_extension}"
# 	file_path = os.path.join(current_app.root_path, 'static/profile_img', image_name)
# 	image.save(file_path)
# 	return image_name

def save_image(image, path=''):
	"""
	Save image into the file system

	Parameters:
		- image (bytes) image to save
		- path (str) path to save the image
	"""
	image_hash = secrets.token_urlsafe(10)
	_, file_extension = os.path.splitext(image.filename)
	image_name = f"{image_hash}{file_extension}"
	
	if path == 'static/blogs_img':
		file_path = os.path.join(current_app.root_path, 'static/blogs_img', image_name)
		image.save(file_path)
		return image_name

	elif path == 'static/profile_img':
		file_path_2 = os.path.join(current_app.root_path, 'static/profile_img', image_name)
		image.save(file_path)
		return image_name


def get_profile_image(image_name):
	"""
	Retrieve profile image from the file system and concat it with the real path

	Returns:
		- The profile image
	"""
    file_path = os.path.join(current_app.root_path, 'static/profile_img', image_name)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            image_data = file.read()
        return image_data
    
    return None


@app.route('/')
def index():
	"""
    Route for the index page.

    Returns:
        - Rendered template for the 'index.html' page.
    """
    return render_template('index.html')

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	"""
    Error handler for 404 - Page Not Found.

    Returns:
        - Rendered template for the '404.html' page.
        - Status code 404.
    """
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	"""
    Error handler for 500 - Internal Server Error.

    Returns:
        - Rendered template for the '500.html' page.
        - Status code 500.
    """
	return render_template("500.html"), 500


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	"""
    Create a new user account.

    Method: POST
    Parameters:
    	- fullname: (str) The desired username for the new account.
        - username: (str) The desired username for the new account.
        - email: (str) The email address of the user.
        - password: (str) The password for the new account.

    Returns:
        - Status code 201 if the account creation is successful.
        - Status code 400 if there are validation errors in the input data.
    """
	from models_sqlite import Users
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
			about_author = "Writer. Explorer. Wordsmith. Unveiling stories one page at a time."

			user = Users(fullname=fullname,
						username=form.username.data,
						about_author=about_author,
			 			email=form.email.data,
			 			profile_pic=save_image(form.profile_pic.data, path='static/profile_img'),
			 			password_hash=hashed_pw)
			try:
				db.session.add(user)
				db.session.commit()
			except Exception as e:
				db.session.rollback()
				return f'{e}'
		form.firstname.data = ''
		form.lastname.data = ''
		form.email.data = ''
		form.password.data = ''
		return	redirect(url_for('login'))
	return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""
	Authenticate a user.

	Methods: GET, POST

	Returns:
		- page with login form
		- Status code 200 if authentication is successful.
        - Status code 401 if authentication fails.
	"""
    from models_sqlite import Users
    form = LoginForm()
    
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                # flash("Login successful")
                # render_template('blogs.html')
                return redirect(url_for('blogs'))
            else:
                flash("Invalid credentials-p")
        else:
            flash("Invalid credentials")
            
    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST'])
@login_required
def logout():
	"""
	log out user

	Method: POST

	returns:
		- Status code 200 if the logout is successful.
        - Status code 401 if the user is not authenticated.

	"""
	logout_user()
	return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
	""""""
	from models_sqlite import Posts
	posts = Posts.query.order_by(Posts.date_posted).all()
	return render_template('dashboard.html', posts=posts, get_short_description=get_short_description)


@app.route('/about')
def about():
	"""
	Learn more about the app

	Method: GET

	Returns:
		- About page
	"""
	return render_template('about.html')


@app.route('/blogs')
def blogs():
	"""
	Retrieve all blogs in the database ordered by the date posted

	Methods: GET

	Returns:
		- page with lists of blogs
	"""
	from models_sqlite import Users, Posts
	search = SearchForm()
	# posts = Posts.query.order_by(desc(Posts.date_posted)).all()
	posts = Posts.query.order_by(Posts.date_posted.desc()).all()

	# user = Users.query.get_or_404(current_user.id)


	return render_template('blogs.html',
							search=search,
							posts=posts,
							get_short_description=get_short_description)

@app.route('/blogs/<int:id>', methods=['GET', 'POST'])
def read_more(id):
	"""
	Retrieve a single blog post with its details
	Retrieve comments for the blog post 

	Methods: GET, POST

	Parameters:
		- id: (int) ID of the post to read

	Returns:
		- page with blog post and its details such as title, image, content and the author details
		- Status code 200 if the comment is added successfully
	"""
	form_action = url_for('read_more', id=id)

	from models_sqlite import Users, Posts, Comments
	form = CommentForm()
	# get the post to render
	post = Posts.query.get_or_404(id)

	# get author profile pic for post rendered
	author_image = Users.query.filter_by(id=post.author_id).value(Users.profile_pic)

	# get comment details for a particular post rendered
	comments_details = db.session.query(Comments, Users.fullname, Users.profile_pic).\
		join(Users, Comments.commenter_id == Users.id).\
		outerjoin(Posts, Comments.post_id == Posts.id).\
		filter(Comments.post_id==post.id).\
		all()

	raw_date = str(post.date_posted)
	date = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S.%f")
	formatted_date = date.strftime('%b %d, %Y')

	if form.validate_on_submit():
		comment = Comments(content=form.comment.data,
							commenter=current_user.fullname,
							commenter_id=current_user.id,
							post_id=post.id)

		try:
			db.session.add(comment)
			db.session.commit()
			return redirect(form_action)
		except Exception as e:
			db.session.rollback()
			return str(e)

	return render_template('read-more.html',
							form_action=form_action,
							form=form,
							post=post,
							author_image=author_image,
							comments_details=comments_details,
							formatted_date=formatted_date)


@app.route('/profile', methods=['GET'])
@login_required
def profile():
	"""
	User profile page 

    Methods: GET

	Returns:
    	- Page with user informations
    """
	from models_sqlite import Users
	id = current_user.id
	user = Users.query.get_or_404(id)

	
	return render_template('profile.html', user=user)


@app.route('/update-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def update_profile(id):
	"""
    Retrieve user data

    Methods: GET, POST
    Parameters:
        - id: (int) The ID of the user to update.

    Returns:
    	- Page with user informations
        - Status code 200 if the user is updated successfully
    """
	form_action = url_for('update_profile', id=id)

	from models_sqlite import Users
	# id = current_user.id
	user = Users.query.get_or_404(id)

	form = SignupForm()

	fullname = user.fullname
	firstname = fullname.split()[0]
	lastname = fullname.split()[1]

	form.firstname.data = firstname
	form.lastname.data = lastname
	form.username.data = user.username
	form.email.data = user.email
	form.about_author.data = user.about_author
	form.profile_pic.data = get_profile_image(user.profile_pic)

	if form.validate_on_submit():
		firstname = form.firstname.data
		lastname = form.lastname.data
		fullname = f'{firstname} {lastname}'
		user.fullname = fullname
		user.username = form.username.data
		user.email = form.email.data
		user.password_hash = user.password_hash
		user.about_author = form.about_author.data
		user.profile_pic = save_profile_image(form.profile_pic.data)

		try:
			db.session.commit()
			return redirect(url_for('profile'))
		except Exception as e:
			db.session.rollback()
			return str(e)

			
	return render_template('update-profile.html', form=form, form_action=form_action, user=user)



@app.route('/update-post/<int:id>', methods=['GET', 'POST'])
@login_required
def update_post(id):
	"""
    Update existing post
    Retrieve the post by its ID

    Methods: GET, POST
    Parameters:
        - id: (int) The ID of the post to update.

    Returns:
        - Status code 200 if the post is updated successfully
    """
	form_action = url_for('update_post', id=id)

	from models_sqlite import Posts
	form = BlogPostForm()

	post_to_update = Posts.query.get_or_404(id)

	if form.validate_on_submit():
		post_to_update.title = form.title.data
		post_to_update.image = save_blogs_image(form.image.data)
		post_to_update.content = form.content.data

		try:
			db.session.commit()
			return redirect(url_for('profile'))
		except Exception as e:
			db.session.rollback()
			return str(e)

	return render_template('update-post.html', form_action=form_action, form=form, post_to_update=post_to_update)


@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
	"""
    Create new post

    Methods: GET, POST

    Returns:
        - Status code 200 if the post is created successfully
    """
	from models_sqlite import Posts
	form = BlogPostForm()
	if form.validate_on_submit():
		title = form.title.data
		image = save_blogs_image(form.image.data)
		description = get_short_description(form.content.data)
		content = form.content.data

		post = Posts(title=title,
					image=image,
					description=description,
					content=content,
					author=current_user.fullname,
					author_id=current_user.id)
		try:
			db.session.add(post)
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			return f'{e}'
		finally:
			db.session.close()
		return redirect(url_for('blogs'))
	return render_template('create-post.html', form=form)



if __name__ == "__main__":
    app.run(debug=True, port=5001)