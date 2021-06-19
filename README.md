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

Currently deployed [here](https://gre-vocab-app.herokuapp.com).
Words are displayed from a pre-populated <b>wordlist.txt</b>, which is the current list of words I am trying to learn. <br>
There is also an option to check the meaning of custom words.