from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'randomish8key'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blogtitle = db.Column(db.String(200))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blogtitle, body, owner):
        self.blogtitle = blogtitle
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref ='owner')
    

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if username and username.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')

def validate_user():
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
    

    username_error = ''
    password_error = ''
    verify_error = ''
   

    if  username == "":
        username_error = 'Please enter Username'
        #username = ''
    else:
        if len(username) < 3 or len(username) > 20:
            username_error = 'Please enter Password with at least 3 characters and 20 or less characters'
            username = ''
        
    if  password == "":
        password_error = 'Please enter Password'
        password = ''
    else:
        if len(password) < 3 or len(password) > 20:
            password_error = 'Please enter Password with at least 3 characters and 20 or less characters'
            password = ''

    if  verify == "":
        verify_error = 'Please verify password'
        verify = ''
    else:
        if verify != password:
            verify_error = 'Verified password must match password'
            verify = ''

        


    if not username_error and not password_error and not verify_error:
        name = username
        return redirect('/index')

    else: 
        return render_template('signup.html', username_error=username_error, 
            password_error=password_error, verify_error=verify_error)


@app.route('/', methods=['POST', 'GET'])
@app.route('/index')
def index():
    return render_template('index.html')
       
@app.route('/blog')
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    return render_template('newpost.html')

@app.route('/addpost', methods=['POST'])
def addpost():
    blogtitle = request.form['blogtitle']
    body = request.form['body']
    
    title_error = ''
    body_error = ''
    
    if blogtitle == "":
        title_error = 'Enter blog title'
   
    if body == "":
        body_error = 'Enter blog post'
    
    if not title_error and not body_error:
        new_blog = Blog(blogtitle=blogtitle, body=body)

        db.session.add(new_blog)
        db.session.commit()
        
        return redirect('/blog')
    
    else:
        return render_template('newpost.html', title_error=title_error, 
        body_error=body_error)

  


@app.route('/single')
def single():
    blog_id = request.args.get('id') 
    blogid = Blog.query.filter_by(id=blog_id).first()
    
    return render_template('single.html', b=blogid)

if __name__ == '__main__':
    app.run()



