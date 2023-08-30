from flask_login import UserMixin
from datetime import datetime
from app import db




class Users(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.String(20), nullable=False, unique=False)
	username = db.Column(db.String(20), nullable=True, unique=True)
	email = db.Column(db.String(120), nullable=False, unique=True)
	password_hash = db.Column(db.String(128))
	about_author = db.Column(db.Text(), nullable=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	profile_pic = db.Column(db.String(20))

    # Define relationship to posts
	posts = db.relationship('Posts', backref='poster', lazy=True)
    # Define relationship to comments
	comments = db.relationship('Comments', backref='comenter', lazy=True)

class Posts(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255), nullable=False)
	image = db.Column(db.String(20))
	description = db.Column(db.Text, nullable=False)
	content = db.Column(db.Text, nullable=False)
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	author = db.Column(db.String(20), nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Define relationship to comments
	comments = db.relationship('Comments', backref='posts', lazy=True)

class Comments(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text, nullable=False)
	date_commented = db.Column(db.DateTime, default=datetime.utcnow)
	commenter = db.Column(db.String(20), nullable=False)
	commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
