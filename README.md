# Vocabulary App
I'm creating this simple Flask app to improve my vocabulary. <br>
Words sourced from this [Excel sheet](https://docs.google.com/spreadsheets/d/1jRATLVV34vATsL4Y67fZZXQc7qZPYc0c0Yk7Bykh4fw/edit#gid=0).

# Requirements

A Heroku acount <br> Python 3.9.0 <br> virtualenv 

# Setup
1. `virtualenv venv`
2. Activate your virtual environment. <br>
   a. `source venv/bin/activate` for Unix <br>
   b.  `venv\Scripts\activate` for Windows
3. `pip install -r requirements.txt`
4. `heroku login`
5. `heroku create`
6. `git push heroku main`

Currently deployed [here](https://nameless-ridge-97165.herokuapp.com).