from flask import Flask, render_template, url_for
from forms import SignupForm, LoginForm, BlogPostForm, SearchForm

app = Flask(__name__)

app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"



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

@app.route('/signup')
def signup():
	signup = SignupForm()
	return render_template('signup.html', signup=signup)

@app.route('/login')
def login():
	login = LoginForm()
	return render_template('login.html', login=login)

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/nav')
def nav():
	# search = SearchForm()
	return render_template('navbar1.html')

@app.route('/blogs')
def blogs():
	search = SearchForm()
	return render_template('blogs.html',  search=search)



if __name__ == "__main__":
    app.run(debug=True)