import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

app = Flask(__name__)

ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
API_KEY_SID = os.environ.get('TWILIO_API_KEY_SID')
API_KEY_SECRET = os.environ.get('TWILIO_API_KEY_SECRET')
AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/createmeet')
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


if __name__ == '__main__':
     app.run(debug=False)
    


