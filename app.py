#-----------------------Import------------------------------
import os
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, current_user

# Reads the key-value pair from .env file and adds them to environment variable
load_dotenv()

#----------------------- GLOBALS ----------------------------
app = Flask(__name__)

# Twilio keys -> used for generating the access tokens for users, that will be used during the meet
ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
API_KEY_SID = os.environ.get('TWILIO_API_KEY_SID')
API_KEY_SECRET = os.environ.get('TWILIO_API_KEY_SECRET')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')

#login manager -> used for user authentication during login
login_manager = LoginManager()
login_manager.init_app(app)

# Database credentials -> used to do CRUD operations on the database
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_INFO')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SQLALCHEMY object
db = SQLAlchemy(app)

# sets the path to the folder where the pdfs are to be saved
app.config['PDF_FOLDER_PATH'] = os.environ.get('PDF_UPLOAD')

# defining User database model
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column("password", db.String(200))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)

class Meet(db.Model):
    __tablename__ = "meet"
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    subject = db.Column("subject", db.String(100))
    topic = db.Column("topic", db.String(100))
    pdf_link = db.Column("pdf_link", db.String(200))

    def __init__(self, name, subject, topic, pdf_link):
        self.name = name
        self.subject = subject
        self.topic = topic
        self.pdf_link = pdf_link

#---------------------- UTIL FUNCTIONS -----------------------
# adds new user to the User database
def add_user(username, email, password):
    print(f"Username:{username}, Email:{email}, Password:{password}")
    # checks if the user already exists before adding to the table
    check_user = User.query.filter_by(email=email).all()
    if check_user != None:
        print("User exists")
        return
    # creates a user object with the given credentials
    user = User(username, email, password)
    # adds the user credentials to the database
    db.session.add(user)
    db.session.commit()
    return

# adds the new meeting to the Meet database
def add_meeting(meet_name, meet_subject, meet_topic, meet_pdf_link):
    # checks if the meeting name already exists
    check_meet = Meet.query.filter_by(name=meet_name).all()
    if len(check_meet) != 0:
        print("Meeting already exists")
        return
    # creates a meet object and adds it to the database
    meet = Meet(meet_name, meet_subject, meet_topic, meet_pdf_link)
    db.session.add(meet)
    db.session.commit()
    return

# checks if the given user email and password are present in the database
def validate_user(user_email, user_password):
    print(f"Email:{user_email}, password:{user_password}")
    # same as the sql query -> "SELECT * FROM users WHERE email=user_email LIMIT 1;"
    user = User.query.filter_by(email=user_email).first()
    # checks if the exists an email corresponding to the given email in the database
    # and if yes then checks if the password hash corresponding to that email
    # matches that of the given password
    if user != None and check_password_hash(user.password, user_password):
        # returns True => validation success and also returns the user credentials
        return True, user
    else:
        # returns False => validation failure
        return False, user

# gets the session id of the particular user with the id provided to the function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#----------------------- ROUTING --------------------------
@app.route('/', methods = ['GET', 'POST'])
@app.route('/home')
def home():
    if request.method == 'POST':
        # gets the email and password entered by the user in the form
        user_email = request.form.get('email')
        user_password = request.form.get('pass')
        # validates the password for the  given email
        validation_result, user_credentials = validate_user(user_email, user_password)
        if validation_result:
            # logs in the user
            login_user(user_credentials)
            return render_template('home.html')
        else:
            return render_template('index.html')
    else:
        # returns the home page if the user is already logged in else returns the login page
        if current_user.is_authenticated:
            return render_template('home.html')
        return render_template('index.html')

@app.route('/signup', methods = ['POST', 'GET'])    
def signup():
    if request.method == 'POST':
        # gets user credentials entered by the user in the form
        user_name = request.form.get('username')
        user_email = request.form.get('email')
        user_password = request.form.get('pass')
        # adds user to the database
        add_user(user_name, user_email, user_password)
        return redirect(url_for('home'))
    else:
        return render_template("signup.html")

@app.route('/join', methods = ['GET', 'POST'])
def join():
    if request.method == 'POST':
        meet_name = request.form.get('link')
        return redirect(url_for('meet', meet_name=meet_name))
    else:
        return render_template('joinlink.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # gets the meeting name from the form
        meet_name = request.form.get('meet_name')
        # gets the subject name from the form
        subject_name = request.form.get('subject')
        # gets the topic name from the form
        topic_name = request.form.get('topic')
        # gets the pdf file uploaded in the form
        pdf_file = request.files.get('pdf_file')
        # saves the pdf file in the set folder with path as above
        pdf_file.save(os.path.join(app.config['PDF_FOLDER_PATH'], secure_filename(pdf_file.filename)))
        print(request.files)
        print('[PDF SAVED]')
        # gets the path of the pdf file where it will be saved 
        path_of_pdf = "uploads/" + secure_filename(pdf_file.filename)
        # adds the meeting details to the meet database
        add_meeting(meet_name, subject_name, topic_name, path_of_pdf)
        return redirect(url_for('meet', meet_name=meet_name))
    else:
        return render_template('upload.html')

@app.route('/meet/<meet_name>')
def meet(meet_name):
    # gets the link to the pdf corresponding to the provided meet name
    meet = Meet.query.filter_by(name=meet_name).first()
    # rendering the html along with the pdf link
    return render_template('meet.html', link_to_pdf = meet.pdf_link)

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
    # creates the database with columns specified by the Users database model if it already does not exist
    db.create_all()
    db.session.commit()
    app.run(debug=True)
    
