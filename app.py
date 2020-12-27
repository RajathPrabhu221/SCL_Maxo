#-----------------------Import------------------------------
import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from flask_sqlalchemy import SQLAlchemy

# Reads the key-value pair from .env file and adds them to environment variable
load_dotenv()

#----------------------- GLOBALS ----------------------------
app = Flask(__name__)

# Twilio keys
ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
API_KEY_SID = os.environ.get('TWILIO_API_KEY_SID')
API_KEY_SECRET = os.environ.get('TWILIO_API_KEY_SECRET')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')

# Database credentials
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_INFO')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SQLALCHEMY object
db = SQLAlchemy(app)

# defining User database model
 class User(db.Model):
    __tablename__ = "users"
    _id = db.Column("id", db.Integer, primary_key=True)
     name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column("password", db.String(20))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

#---------------------- UTIL FUNCTIONS -----------------------
# adds new user to the database
def add_user(username, email, password):
    print(f"Username:{username}, Email:{email}, Password:{password}")
    user = User(username, email, password)
    db.session.add(user)
    db.session.commit()
    return

# # checks if the given user email and password are present in the database
def validate_user(user_email, user_password):
    print(f"Email:{user_email}, password:{user_password}")
    # same as "SELECT * FROM users WHERE email=user_email AND password=user_password;"
    user = User.query.filter_by(email=user_email, password=user_password).all()
    if len(user) != 0:
        return True
    else:
        return False

#----------------------- ROUTING --------------------------
@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['pass']
        if validate_user(user_email, user_password):
            print("Logged in")
            return redirect(url_for('create'))
        else:
            print("Invalid credentials")
            return render_template('index.html')
    else:
        return render_template('index.html')

@app.route('/signup', methods = ['POST', 'GET'])    
def signup():
    if request.method == 'POST':
        user_name = request.form['username']
        user_email = request.form['email']
        user_password = request.form['pass']
        add_user(user_name, user_email, user_password)
        return render_template("index.html")
    else:
        return render_template("signup.html")

@app.route('/create')
def create():
    return render_template('home.html')

@app.route('/join')
def join():
    return render_template('joinlink.html')

# generating api key for a user which is used to connect to a room 
# If a room already exists then using this token enables a person to join the room if it doesnot exist then a  room is created
@app.route('/gen_token', methods = ['POST'])
def api_token_gen():
    #get the username and roomname from the frontend
    user_name = request.get_json(force = True).get('username')
    room_name = request.get_json(force = True).get('roomname')
    # Create an Access Token
    token = AccessToken(ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET, identity = user_name)
    # Create a video grant and add it to the token
    grant = VideoGrant(room = room_name)
    token.add_grant(grant)
    # Serialize the token as a JWT(json web token) i.e converts token to json which can be returned to the frontend
    jwt = token.to_jwt().decode()
    print(f"Created token for {user_name}, room:{room_name} ",jwt)
    return {'token':jwt}

#-------------------------------Execution starts here------------------------------------------------
if __name__ == '__main__':
    creates the database with columns specified by the Users database model if it alredy does not exist
    db.create_all()
    db.session.commit()
    app.run(debug=True)
    


