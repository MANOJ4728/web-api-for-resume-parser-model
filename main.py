from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from pymongo import MongoClient
import spacy

nlp = spacy.load("en_core_web_lg")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['credentials']
users = db['clients']

# Load your SpaCy model
nlp = spacy.load("C:/Users/manoj.rokkala/Desktop/app/model-best-20231016T080818Z-001/model-best")

# Define Flask-WTF forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class ResumeForm(FlaskForm):
    resume_text = TextAreaField('Resume Text', validators=[DataRequired()])
    submit = SubmitField('Parse Resume')

# Define routes
@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Retrieve user input
        username = form.username.data
        password = form.password.data

        # Check if the user exists in the MongoDB database
        user = users.find_one({'username': username, 'password': password})

        if user:
            flash('Login successful', 'success')
            return redirect('/resume_insert')
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Retrieve user input
        username = form.username.data
        password = form.password.data

        # Check if the username already exists
        existing_user = users.find_one({'username': username})

        if existing_user is None:
            # If the username is unique, add the new user to MongoDB
            users.insert_one({'username': username, 'password': password})
            flash('Registration successful', 'success')
            return redirect('/login')
        else:
            flash('Username already exists', 'danger')

    return render_template('register.html', form=form)

@app.route('/resume_insert', methods=['GET', 'POST'])
def resume_insert():
    form = ResumeForm()
    if request.method == 'POST':
        resume_text = form.resume_text.data
        parsed_data = process_with_model(resume_text)
        return render_template('result_page.html', parsed_data=parsed_data)
    return render_template('resume_insert.html', form=form)


def process_with_model(resume_text):
    doc = nlp(resume_text)
    parsed_data = {}

    for ent in doc.ents:
        entity_text = ent.text
        label = ent.label_
        
        if label in parsed_data:
            parsed_data[label].append(entity_text)
        else:
            parsed_data[label] = [entity_text]

    return parsed_data



if __name__ == '__main__':
    app.run(debug=True)
