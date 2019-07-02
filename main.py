from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):  

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog')
def index():

    posts = Blog.query.all()

    return render_template('blog.html', title='Build A Blog', posts=posts)

#Checks if post fields (title or body) are blank
def validate_field(field):
    a_field = field.strip()
    return a_field == ''


@app.route('/newpost', methods=['POST','GET'])
def new_post():

    title_error = ''
    body_error = ''
    post_title = ''
    post_body = ''

    #Runs if a new post is submitted
    if request.method == 'POST':

        post_title = request.form['title']
        post_body = request.form['body']

        if validate_field(post_title):
            title_error = "Please enter a title!"
            post_title = ''
        if validate_field(post_body):
            body_error = "Please enter the body contents!"
            post_body = ''



        if not validate_field(post_title) and not validate_field(post_body):

            post = Blog(post_title,post_body)
            db.session.add(post)
            db.session.commit()
            return redirect('/blog')
        
        else:
            return render_template('newpost.html',
                title='New Post',
                title_error=title_error,
                body_error=body_error,
                post_title=post_title,
                post_body=post_body)


        return render_template('newpost.html',
            title='New Post',
            title_error=title_error,
            body_error=body_error,
            post_title=post_title,
            post_body=post_body)


if __name__ == '__main__':
    app.run()