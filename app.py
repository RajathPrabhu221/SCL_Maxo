from flask import Flask, render_template
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('login.html')



@app.route('/signup')
def signup():
    return render_template("signin.html")

if __name__ == '__main__':
    app.run(debug=False)
    


