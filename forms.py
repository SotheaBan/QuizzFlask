from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo,URL
from wtforms import BooleanField
from flask_wtf.file import FileField, FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=25)])
    avatar = FileField('Upload Avatar', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Only image files are allowed!')
    ])
    submit = SubmitField('Save Changes')



class QuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=10, max=255)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=30)])
    tags = StringField('Tags (comma-separated)', validators=[DataRequired(), Length(max=255)])
    
    image = FileField('Attach Image (optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed.')
    ])
    
    submit = SubmitField('Post Question')

class AnswerForm(FlaskForm):
    answer = TextAreaField('Your Answer', validators=[
        DataRequired(), Length(min=10)
    ])
    submit = SubmitField('Post Answer')