#-----------------------Import------------------------------
import os
import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_socketio import SocketIO, emit, join_room
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail, Message


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
# sets the login page render function as the function -> index 
# to which a page is redirected if the user has not logged in and the page requires login
login_manager.login_view = 'index'

# Database credentials -> used to do CRUD operations on the database
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_INFO')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SQLALCHEMY object
db = SQLAlchemy(app)

# sets the path to the folder where the pdfs are to be saved
app.config['PDF_FOLDER_PATH'] = os.environ.get('PDF_UPLOAD')

# socketio object
socketio = SocketIO(app)

# mail credentials
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_ID')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

# defining structure of the users table
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

# defining structure of the meet table
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

# defining structure of the comments table
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column("id", db.Integer, primary_key=True)
    content = db.Column("content", db.Text)
    user = db.Column("user", db.String(100))
    date = db.Column("date",db.DateTime)

    def __init__(self, content, user):
        self.content = content
        self.user = user
        self.date = datetime.datetime.now()

# defining structure of the threads table
class Thread(db.Model):
    __tablename__ = "threads"
    id = db.Column("id", db.Integer, primary_key=True)
    comment_id = db.Column("comment_id", db.Integer)
    content = db.Column("content", db.Text)
    user = db.Column("user", db.String(100))
    date = db.Column("date",db.DateTime)

    def __init__(self, comment_id, content, user):
        self.comment_id = comment_id
        self.content = content
        self.user = user
        self.date = datetime.datetime.now()


#---------------------- UTIL FUNCTIONS -----------------------
# adds new user to the User database
def add_user(username, email, password):
    check_user = User.query.filter_by(email=email).first()
    # checks if the user already exists before adding to the table, is same as -> select * from users where email = email;
    if check_user != None:
        return False
    # creates a user object with the given credentials
    user = User(username, email, password)
    # adds the user credentials to the database
    db.session.add(user)
    db.session.commit()
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] ADDED USER:{username} EMAIL:{email}")
    return True

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
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] MEETING CREATED MEET NAME:{meet_name} SUBJECT:{meet_subject} TOPIC:{meet_topic}")
    return

# checks if the given user email and password are present in the database
def validate_user(user_email, user_password):
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

# checks whether the extension of a file is a valid extension  
def validate_extension(file_name):
    valid_extensions = ['pdf']
    # splits the file name at '.'
    file_extension = file_name.split('.')
    # returns true if its a valid extension eles return false
    if file_extension[-1].lower() in valid_extensions and len(file_extension) < 3:
        return True
    return False

# adds the comment to the comment database
def add_comment(comment_content, user_name):
    # creates a comment object
    comment = Comment(comment_content, user_name)
    # adds the comment object to the database and commits it
    db.session.add(comment)
    db.session.commit()
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] ADDED COMMENT BY USER:{user_name}")
    return comment

def add_thread(thread_content, comment_id, user_name):
    # creates a thread object
    thread = Thread(comment_id, thread_content, user_name)
    # adds the thread to the database and commits it
    db.session.add(thread)
    db.session.commit()
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] THREAD ADDED TO COMMENT_ID:{comment_id} USER:{user_name}")
    return thread

def get_reset_token(user_id):
    # creates a serializer with a secret key which is used to serialize the id of the user that wants to reset his/her password
    serializer = Serializer(app.config['SECRET_KEY'], 1000)
    # serializes the user id (i.e encrpyts the user id so that it can be sent to the user through mail which then can be used as a token to verify the user when changing the password)
    token = serializer.dumps({'id':user_id}).decode('utf-8')
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] PASSWORD RESET TOKEN CREATED FOR USER_ID:{user_id}")
    return token

def verify_reset_token(token):
    # the secret key is used to decrypt the token through the serializer
    serializer = Serializer(app.config['SECRET_KEY'])
    try:
        # gets the user id from the token
        # user id can only be obtained from the token only if the token is verified before expiry else an error is thrown
        user_id = serializer.loads(token)['id']
    except:
        # if an error is thrown it implies that the token has expired
        return None
    # token has not expired and contains the user id
    return user_id

def send_reset_email(user_id, user_email):
    # creates a new token from the user id
    token = get_reset_token(user_id)
    # sets the mail sender, mail reciever
    msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[user_email])
    # sets the body of the mail
    msg.body = f'''To reset your password, visit the following link:
{url_for('change_password',token=token, _external=True)}'''   
    # sends the mail
    mail.send(msg)
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] MAIL SENT TO EMAIL:{user_email}")
    return

# gets the session id of the particular user with the id provided to the function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 
#----------------------- ROUTING --------------------------
@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        # gets the email and password entered by the user in the form
        user_email = request.form.get('email')
        user_password = request.form.get('pass')
        # validates the password for the  given email
        validation_result, user_credentials = validate_user(user_email, user_password)
        if validation_result:
            time = datetime.datetime.now()
            print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] LOGGEDIN:{user_email}")
            # logs in the user
            login_user(user_credentials)
            return redirect(url_for('home'))
        else:
            flash('Invalid user email or password', category='danger')
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
        if add_user(user_name, user_email, user_password):
            flash('Account created please login', category='success')
            return redirect(url_for('index'))
        else:
            flash('You already have an account please login')
            return render_template('signup.html') 
    else:
        return render_template('signup.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/join', methods = ['GET', 'POST'])
@login_required
def join():
    if request.method == 'POST':
        # gets the meet name from the form
        meet_name = request.form.get('link')
        time = datetime.datetime.now()
        print(f"127.0.0.1 - - [{time.day:02d}/{time.strftime('%b')}/{time.year} {time.hour:02d}:{time.minute:02d}:{time.second:02d}] JOINED MEET USER:{current_user.name}")
        # redirects to the meet with the above meet name
        return redirect(url_for('meet', meet_name=meet_name))
    else:
        return render_template('joinlink.html')

@app.route('/upload', methods = ['GET', 'POST'])
@login_required
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
        # validates if the file is a pdf
        meet = Meet.query.filter_by(name=meet_name).first()
        if meet != None:
            flash("Please create a meeting with different name. This meeting already exists")
            return render_template('upload.html')
        if validate_extension(secure_filename(pdf_file.filename)):
            # saves the pdf file in the set folder with path as above
            pdf_file.save(os.path.join(app.config['PDF_FOLDER_PATH'], secure_filename(pdf_file.filename)))
            # gets the path of the pdf file where it will be saved 
            path_of_pdf = "uploads/" + secure_filename(pdf_file.filename)
            # adds the meeting details to the meet database
            add_meeting(meet_name, subject_name, topic_name, path_of_pdf)
            time = datetime.datetime.now()
            print(f"127.0.0.1 - - [{time.day}/{time.strftime('%b')}/{time.year} {time.hour}:{time.minute}:{time.second}] NEW MEETING CREATED MEET_NAME:{meet_name} SUBJECT:{subject_name} TOPIC:{topic_name}")
            return redirect(url_for('meet', meet_name=meet_name))
        # if the file is not a pdf a message is sent to the user
        else:
            flash("Please upload only pdf files")
            return render_template('upload.html')
    else:
        return render_template('upload.html')

@app.route('/meet/<meet_name>')
@login_required
def meet(meet_name):
    # gets the link to the pdf corresponding to the provided meet name
    meet = Meet.query.filter_by(name=meet_name).first()
    # rendering the html along with the pdf link
    return render_template('meet.html', link_to_pdf = meet.pdf_link)

# generating api key for a user which is used to connect to a room 
# If a room already exists then using this token enables a person to join the room if it doesnot exist then a  room is created
@app.route('/gen_token', methods = ['POST'])
@login_required
def api_token_gen():
    #get the username and roomname from the frontend
    user_name = current_user.name
    # gets the room name from url
    room_name = request.get_json(force = True).get('url').split('/')[-1]
    # Creates an Access Token
    token = AccessToken(ACCOUNT_SID, API_KEY_SID, API_KEY_SECRET, identity = user_name)
    # Creates a video grant and adds it to the token
    grant = VideoGrant(room = room_name)
    token.add_grant(grant)
    # Serializes the token as a JWT(json web token) i.e converts token to json which can be returned to the frontend
    jwt = token.to_jwt().decode()
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] TOKEN GENERATED USER:{current_user.name} FOR ROOM:{room_name}")    
    # return both the token and room name as a json
    return {'token':jwt, 'roomname':room_name}

@app.route('/discuss', methods = ['GET'])
@login_required
def discuss():
    # gets all the comments in the database as per their chronological order, same as -> SELECT * FROM comments ORDER BY date;
    comments = Comment.query.order_by(Comment.date)    
    return render_template('Discuss.html', comments=comments)

@socketio.on('commented')
def comment_handler(comment_content):
    # adds the comment to the database
    comment = add_comment(comment_content, current_user.name)
    date = f'{comment.date.year}-{comment.date.month:02d}-{comment.date.day:02d} {comment.date.hour:02d}:{comment.date.minute:02d}:{comment.date.second:02d}'
    # returns the information related to the comment to the frontend where it is dynamically added
    emit('commented',{'user':comment.user, 'date':date,'content':comment.content, 'id':comment.id}, broadcast=True)

@app.route('/reply')
def reply():
    # gets the comment id from the get request parameters
    comment_id = int(request.args.get('comment_id'))
    # gets the comment corresponding to the 
    comment = Comment.query.filter_by(id = comment_id).first()
    # gets all the threads(replies) corresponding to the above comment as per their chronological order, same as -> SELECT * FROM threads WHERE comment_id=comment_id ORDER BY date;
    threads = Thread.query.filter_by(comment_id=comment_id).order_by(Thread.date)
    # the comment and the replies are rendered
    return render_template("Reply.html", comment=comment, threads=threads)

@socketio.on('join-room')
def join_room_handler(data):
    # gets the room id from the data sent by frontend
    room = int(data.split('=')[-1])
    # adds the user to the room specified by room id
    join_room(room)
    # emits  the joined room event back to the user
    emit('joined-room', room)

@socketio.on('replied')
def reply_handler(thread_data):
    # gets the room id from the thread data sent by frontend
    room = thread_data['thread_room']
    # gets the thread content
    thread_content = thread_data['thread_content']
    # adds the thread to the database
    thread = add_thread(thread_content, room, current_user.name)
    date = f'{thread.date.year}-{thread.date.month:02d}-{thread.date.day:02d} {thread.date.hour:02d}:{thread.date.minute:02d}:{thread.date.second:02d}'
    # emits replied event which updates the reply in the frontend
    emit('replied', { 'user':thread.user, 'date':date, 'content':thread.content }, room=room)

@app.route('/log_out')
@login_required
def log_out():
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] LOGGED OUT USER:{current_user.name}")
    # logs out an user
    logout_user()
    return redirect(url_for('index'))

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        # gets the recovery email from the form
        recovery_email = request.form.get('email')
        user = User.query.filter_by(email=recovery_email).first()
        # checks if a user with the above email is present
        if user != None:
            # if user exists, a password reset mail is sent
            send_reset_email(user.id, user.email)
            flash('Please check your email')
            return render_template('password_reset.html')
        else:
            # if no such user exits, then a warning is sent
            flash('There is no account with that email. You must register first.')
            return render_template('password_reset.html')
    else:
        return render_template('password_reset.html')

@app.route('/change_password/<token>', methods=['GET', 'POST'])
def change_password(token):
    # verifies the token and gets the user id from it
    user_id  = verify_reset_token(token)
    if request.method == 'POST':
        if user_id != None:
            # gets the new password from the form
            new_password = request.form.get('password')
            # gets the user id with user id in token
            user = User.query.filter_by(id=user_id).first()
            # changes the password of the user and adds it to the database
            user.password = generate_password_hash(new_password)
            # commits the changes to the database
            db.session.commit()
            time = datetime.datetime.now()
            print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] NEW PASSWORD SET FOR USER_ID:{user_id}")
            flash('Password updated', category='success')
            return redirect(url_for('index'))
        else:
            flash("The password link expired, please send the request again")
            return redirect(url_for('reset'))
    else: 
        if user_id != None:
            # if the token is verified then the page which resets password is rendered
            return render_template('new_password.html')
        else :
            # if the token verification fails then a warning is sent
            flash("The password link expired, please send the request again")
            return redirect(url_for('reset'))

@socketio.on('join-video-room')
def video_room_handler(video_room_data):
    # gets the room from the data sent by the frontend
    room = video_room_data.split('/')[-1]
    # adds a user to the room which corresponds to a particular meeting (which will be used to send the quizzes to all the connected participants)
    join_room(room)
    emit('joined-video-room', room)

@socketio.on('quiz')
def quiz_handler(quiz_data):
    # gets the room to which the meeting belongs
    room = quiz_data['room']
    # gets the link to the quiz page (posted by the professor)
    quiz_link = quiz_data['link']
    time = datetime.datetime.now()
    print(f"127.0.0.1 - - [{time.day:02}/{time.strftime('%b')}/{time.year} {time.hour:02}:{time.minute:02}:{time.second:02}] QUIZ STARTED AT ROOM:{room}")
    # sends the link to all the participants connected to the room
    emit('quiz', quiz_link, room=room)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404 page.html')

#-------------------------------Execution starts here------------------------------------------------
if __name__ == '__main__':
    # creates the database with columns specified by the users, meet, comments and threads  database model if it already does not exist
    db.create_all()
    db.session.commit()
    socketio.run(app)
    
