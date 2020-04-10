from flask import Flask, render_template, request,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from werkzeug.utils import secure_filename
from flask_mail import Mail
import os
import math
# making configurable json file
localhost = True
c = open("C:/Users/MY PC/PycharmProjects/TheShubhCode web design/templates/config.json", 'r')
param = json.load(c)["param"]

app = Flask(__name__)
app.secret_key='super secret key'
app.config["UPLOAD_FOLDER"] = param['upload_location']

# sending an email when someone fill contact form
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = param['my_gmail'],
    MAIL_PASSWORD=  param['pass']
)

mail = Mail(app)

if (localhost):
    app.config['SQLALCHEMY_DATABASE_URI'] = param['local_server']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['prod_server']
db = SQLAlchemy(app)
"""name	phno	email	message	date"""
# creating contact class for contact form

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phno = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(120), nullable=False)

# creating class for post

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    image_file = db.Column(db.String(12), nullable=False)
    tag_file = db.Column(db.String(12), nullable=False)

@app.route("/")
def HomePage():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(param['noofposts']))

    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page - 1) * int(param['noofposts']): (page - 1) * int(param['noofposts']) + int(param['noofposts'])]
    # first page
    if (page == 1):
        prev = "#"
        next = "/?page=" + str(page + 1)
    # on last page
    elif (page == last):
        prev = "/?page=" + str(page - 1)
        next = "#"
    # middle page
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template('index.html', param=param, posts=posts, prev=prev, next=next)


@app.route("/about")
def about():
    return render_template("about.html",param=param)

# post data
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', param=param, post=post)

# file uploader
@app.route("/uploader", methods=['GET','POST'])
def upload():
    if ('user' in session and session['user'] == param['admin_user']):
             if (request.method == 'POST'):
                 f = request.files['file1']
                 f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
                 return "Uploaded successfully"

# function to add User information in database

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method == "POST"):
        '''add entry in to data base'''
        Name = request.form.get('Name')
        phonenom = request.form.get('phonenom')
        email = request.form.get('email')
        message = request.form.get('message')
        entry = Contacts(name=Name, phno=phonenom, email=email, message=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + Name,
                          sender=email,
                          recipients=[param['my_gmail']],
                          body=message + "\n" + phonenom
                          )
        flash('Thanks for submitting your details. We will contact back you soon!','success')
    return render_template("contact.html",param=param)

# make functionable to our Dashboard

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    if ('user' in session and session['user'] == param['admin_user']):
        posts = Posts.query.all()
        return render_template ('dashboard.html', param=param, posts=posts)


    if request.method=='POST':
            username = request.form.get('uname')
            userpass = request.form.get('pass')
            if (username == param['admin_user'] and userpass == param['admin_password']):
                session['user'] = username
                posts = Posts.query.all()
                return render_template('dashboard.html', param=param, posts = posts)

    return render_template('login.html', param=param)

# function for adding new post or to edit existing post

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == param['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('Title')
            tline = request.form.get('tag_file')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('image_file')
            date = datetime.now()

            if sno=='0':
                post = Posts(Title=box_title, slug=slug, content=content, tag_file=tline, image_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.Title = box_title
                post.slug = slug
                post.content = content
                post.tag_file = tline
                post.image_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', param=param, post=post, sno=sno)

# make functional to logOut button

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

# function to delete our post

@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
    if 'user' in session and session['user']==param['admin_user']:
         post = Posts.query.filter_by(sno=sno).first()
         db.session.delete(post)
         db.session.commit()
    return redirect('/dashboard')

app.run(debug=True)
