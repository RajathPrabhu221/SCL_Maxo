from flask import Flask, render_template
app = Flask(__name__)
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

if __name__ == '__main__':
     app.run(debug=False)
    


