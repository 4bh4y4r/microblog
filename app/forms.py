from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Post


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired( message="Cannot be empty"), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired( message="Cannot be empty"), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Please use a different username')
        

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('Please use a different email')
        

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])

    about_me = StringField('About Me', validators=[Length(min=2, max = 400)])

    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self,username):

        if username.data != self.original_username:

            user = User.query.filter_by(username= username.data).first()

            if user:
                raise ValidationError("Please use a different username")
            

class PostForm(FlaskForm):

    content = TextAreaField("What's on your mind?", validators=[Length(min=2, max = 500)])
    submit  = SubmitField("Post")