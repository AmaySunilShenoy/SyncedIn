from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_wtf.file import FileAllowed, FileRequired

class SignUpForm(FlaskForm):
    def __init__(self, existing_usernames=None, existing_emails=None):
        super(SignUpForm, self).__init__()
        self.existing_usernames = existing_usernames
        self.existing_emails = existing_emails

    firstname = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=20)
        ])
    
    lastname = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=20)
        ])

    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=5, max=15)
        ])
    
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])

    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5, max=20),
        
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    profile_picture = FileField('Profile Picture')

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if self.existing_usernames:
            if username.data in self.existing_usernames:
                raise ValidationError('This username is already in use! Please choose another username')

    def validate_email(self, email):
        if self.existing_emails:
            if email.data in self.existing_emails:
                raise ValidationError('This email address is already registered with an account!')


class LogInForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=5, max=15)
        ])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=5, max=20)
    ])

    submit = SubmitField('Log In')


class ApplicationForm(FlaskForm):

    firstname = StringField('First Name', validators=[
        DataRequired(),
        Length(min=2, max=20)
        ])
    lastname = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=2, max=20)
        ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    phone = IntegerField('Phone Number', validators=[
        DataRequired(),
        ])
    address = StringField('Address', validators=[
        DataRequired(),
        Length(min=10, max=100)
        ])
    
    cv = FileField('Upload CV', validators=[FileAllowed(['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'])])

    comments = TextAreaField('Comments', validators=[
        Length(min=0, max=100)
        ])
    
    submit = SubmitField('Apply for Position')