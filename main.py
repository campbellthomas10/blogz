from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'doy1384gpasp&dp934n'

class Blog(db.Model):  

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return "<Body: " + self.body +">"

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(20))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

#Checks if post fields (title or body) are blank
def validate_post(post):
    a_field = post.strip()
    return a_field == ''
#Checks if password is bewteen 3 - 20 characters and has no spaces.
def validate_password(password):
    if len(password) < 21 and len(password) > 2:
        for letter in password:
            if letter == ' ':
                return False
        return True
    else:
        return False

#Checks if email is valid
def validate_email(email):
    if email.find('@') > 0:
        if email.rfind('.') > 0:
            if email.find('@') < email.rfind('.'):
                return True
    return False


#Checks if they are logged in, if not, redirect to /login
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

#Login Page and if validates they exist.
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user'] = email
            flash('Logged in!')
            return redirect('/')
        else:
            flash("Incorrect password, or user doesn't exist.", 'error')
    return render_template('login.html', title='Login')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verified']

        #Error message for invalid email
        if not validate_email(email):
            flash('Invlaid Email!', 'error')

        #Error message for invalid password
        if not validate_password(password):
            flash('Invalid Password!', 'error')

        #Error message for mismatching password and verification password
        if verify != password:
            flash('Passwords do not match!', 'error')

        existing_user = User.query.filter_by(email=email).first()
        if validate_email(email) and validate_password(password) and verify == password:
            if not existing_user:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                return redirect('/')
            flash('Email already in use!', 'error')
            return render_template('register.html', title='Register')
    return render_template('register.html',title='Register')

#Logout route
@app.route('/logout')
def logout():
    del session['user']
    return redirect('/')


#Displays the main blog page with all authors (as of now)
#TODO - Add filter by author
@app.route('/')
def index():
    posts = Blog.query.all()
    return render_template('blog.html', title='Blogz', posts=posts)


#Displays page to create a new post.
@app.route('/newpost', methods=['POST','GET'])
def new_post():

    post_title = ''
    post_body = ''

    #Runs if a new post is submitted
    if request.method == 'POST':

        post_title = request.form['title']
        post_body = request.form['body']

        if validate_post(post_title):
            flash('Please enter a title!', 'error')
            post_title = ''
        if validate_post(post_body):
            flash('Please enter something into the body!', 'error')
            post_body = ''

        if not validate_post(post_title) and not validate_post(post_body):
            owner = User.query.filter_by(email=session['user']).first()
            post = Blog(post_title,post_body, owner)
            db.session.add(post)
            db.session.commit()
            return redirect('./post?id={}'.format(post.id))
        
        else:
            return render_template('newpost.html',
                title='New Post',
                post_title=post_title,
                post_body=post_body)


    return render_template('newpost.html',
        title='New Post',
        post_title=post_title,
        post_body=post_body)


#Indiviual page
@app.route('/post', methods=['GET'])
def post():
    owner = User.query.filter_by(email=session['user']).first()
    id = request.args.get('id')
    post = Blog.query.filter_by(id=id,owner_id=owner.id).first()
    return render_template('post.html',title=post.title, body=post.body)


if __name__ == '__main__':
    app.run()