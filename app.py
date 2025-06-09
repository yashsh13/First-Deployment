from flask import Flask,render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://uafgt0st6b4cczlj:p2CSGw1StaAIaID5iFmH@bhevoq5tgymj1grvsn0x-mysql.services.clever-cloud.com:3306/bhevoq5tgymj1grvsn0x"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='hahaha'

db = SQLAlchemy(app)

class Posts(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    heading = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(10000), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)

class Accounts(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)


@app.route("/")
def home():

    posts = Posts.query.all()
    if session:
        logged_in=1
        logged_out=0
        account = Accounts.query.filter_by(email=session['email']).first() 
    else:
        logged_in=0
        logged_out=1
        account='lund mera'

    return render_template('home.html',posts=posts,logged_in=logged_in,logged_out=logged_out,account=account)

@app.route("/posts",methods=['GET','POST'])
def posts():

    if session:
        if request.method == 'POST':
            
            username = session['username']
            heading = request.form['heading']
            content = request.form['content']
            date = time.ctime(time.time())
            slug = username.split(' ')[0].lower() + date.replace(' ','')
            
                

            entry = Posts(username=username,heading=heading,content=content,date=date,slug=slug)

            db.session.add(entry)
            db.session.commit()
        
        posts = Posts.query.filter_by(username=session['username']).all()

        return render_template('posts.html',posts=posts)
    else:
        session['from_post']=1
        return redirect('/login')

@app.route("/page/<string:slug>")
def page(slug):

    post = Posts.query.filter_by(slug=slug).first()
    return render_template('page.html',post=post)

@app.route('/register',methods=['GET','POST'])
def register():

    val = 0

    if request.method == 'POST':
        
        
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        entry = Accounts(username=username,email=email,password=password)
        db.session.add(entry)
        db.session.commit()
        val=1

    return render_template('register.html',val=val)

@app.route('/login',methods=['GET','POST'])
def login():

    from_post = 0
    invalid=0

    if session:
        from_post = session['from_post']
        session.pop('from_post',None)

    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']

        if (Accounts.query.filter_by(email=email).first()) and (password == Accounts.query.filter_by(email=email).first().password):

            session['email'] = email
            session['username'] = Accounts.query.filter_by(email=email).first().username
            invalid=0
            return redirect('/')
        invalid=1

    return render_template('login.html',from_post=from_post,invalid=invalid)

@app.route("/logout",methods=['POST','GET'])
def logout():

    session.pop('email',None)
    session.pop('username',None)
    
    return redirect('/')

@app.route('/edit/<string:slug>',methods=['POST','GET'])
def edit(slug):

    post = Posts.query.filter_by(slug=slug).first()

    try:
        if session['username'] == post.username:

            post = Posts.query.filter_by(slug=slug).first()

            if request.method == 'POST':

                post.heading = request.form['heading']
                post.content = request.form['content']

                db.session.commit()

                return redirect('/posts')

            return render_template('edit.html',post=post)

        else :
            return render_template('hacker.html')
    
    except :
        return render_template('hacker.html')


@app.route('/delete/<string:slug>',methods=['POST','GET'])
def delete(slug):

    post  = Posts.query.filter_by(slug=slug).first()

    try:
        if session['username'] == post.username:
            db.session.delete(post)
            db.session.commit()
            return redirect('/posts')

        else:
            return render_template('hacker.html')
    except:
        return render_template('hacker.html')
        
if '__main__' == __name__:
    app.run()