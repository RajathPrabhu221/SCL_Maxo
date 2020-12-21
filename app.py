from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

def validate_signin(email, password):
    return True
    
@app.route('/', methods = ["POST","GET"])
def home():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["pass"]
        #print(user_email, user_password)
        if validate_signin(user_email, user_password):
            return create()
        else:
            return render_template('index.html')
    else:
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

if __name__ == '__main__':
     app.run(debug=False)
    


