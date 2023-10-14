from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NoneOf

class SignUpForm(FlaskForm):
    def __init__(self, existing_usernames=None, existing_emails=None):
        super(SignUpForm, self).__init__()
        self.existing_usernames = existing_usernames
        self.existing_emails = existing_emails

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
        Length(min=5, max=20)
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

    profile_picture = FileField('Profile Picture')

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if username.data in self.existing_usernames:
            raise ValidationError('This username is already in use! Please choose another username')

    def validate_email(self, email):
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


class PaymentForm(FlaskForm):
    address = TextAreaField('Address', validators=[
        DataRequired(),
        Length(min=5,max=100)
    ])
    card_number = StringField('Card Number', validators=[
        DataRequired(),
        Length(min=16,max=16)
    ])

    expiry_date = StringField('Expiry Date', validators=[
        DataRequired(),
        Length(min=5,max=5)
    ])

    cvv = StringField('CVV', validators=[
        DataRequired(),
        Length(min=3,max=3)
    ])

    submit = SubmitField('Place Order')