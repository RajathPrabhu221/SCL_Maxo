
 # Ne-Meet <img src="static/images/Final-Logo.png" border="0" width= 50>
 
A video conference app oriented towards better digital education. The app provides seamless video streaming with quality notes running at the same time. This is completely inclined towards the betterment of the students.

## Project Description

#### Languages Used:

1) Python <a href="https://www.python.org/" ><img src="https://github.com/Sudarshan-Mech/SCL_Maxo/blob/main/static/images/python%20logo.png" width= 30></a>
2) HTML <a href="https://developer.mozilla.org/en-US/docs/Web/HTML"><img src="static/images/HTML%20logo%20Modified.png" width= 30></a>
3) CSS  <a href="https://developer.mozilla.org/en-US/docs/Web/CSS"><img src="https://github.com/Sudarshan-Mech/SCL_Maxo/blob/main/static/images/CSS%20logo.png" width= 30></a>
4) Java Script <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript"><img src="static/images/javascript%20modified.png" width= 30></a>
5) Sass CSS (SCSS) <a href="https://sass-lang.com/"><img src="https://github.com/Sudarshan-Mech/SCL_Maxo/blob/main/static/images/SCSS%20logo.jpg" width= 50></a>
6) Flask <a href="https://flask.palletsprojects.com/en/1.1.x/"><img src="static/images/Flask%20logo%20Modified.jpg" width= 35></a>
7) Twilio <a href="https://www.twilio.com/docs/video/javascript-getting-started"><img src="https://github.com/RajathPrabhu221/SCL_Maxo/blob/main/static/images/Twilio%20logo%20Modified.png" width= 40></a>
8) Socket-io <a href="https://socket.io/"><img src="static/images/Socket-io.svg" width= 35></a>
9) MySQL <a href="https://www.mysql.com/"><img src="static/images/my%20sql.png" width= 50></a>


## Installation 

1. Fork and Clone
    <ol>
    <li>Fork the Repo</li>
    <li>Clone the repo to you computer.</li>
    </ol>

2. Create a Virtual Environment for the Project

    In Windows
    ```bash
    python -m venv venv
    
    venv\Scripts\activate
    ```

    In Ubuntu/MacOS
    ```bash
    python -m virtualenv venv
    
    source venv/bin/activate
    ```
   
   If you are giving a different name then `venv`, then please mention it in `.gitigonre` first

3. Install all the requirements

    ```bash
    pip install -r requirements.txt
    ```
    
4. Create a file called .env and copy the contents from envtemplate to it.
   Change the config parameters
   ```dosini
   # api keys
   TWILIO_ACCOUNT_SID='your twilio account sid'
   TWILIO_API_KEY_SID='your twilio api key sid'
   TWILIO_API_KEY_SECRET='your twilio api secret'
   TWILIO_AUTH_TOKEN ='your twilio api auth token'

   #database credentials
   SECRET_KEY='your secret key'
   DATABASE_INFO='mysql://usernmame:password@server/database'

   PDF_UPLOAD='absolute path to the folder where the pdfs are to be saved'
   ```
   
5.  Execute ```bash python app.py ``` to start the server

6. Do the Development and send me a PR referencing the issue.
   

## Contributing
   Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

