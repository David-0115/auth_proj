from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
import email_validator
from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
                           InputRequired(), Length(min=4, max=20)])

    password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=8)])

    email = EmailField("Email", validators=[
                       InputRequired(), Email(), Length(max=50)])

    first_name = StringField("First Name", validators=[
                             InputRequired(), Length(max=30)])

    last_name = StringField("Last Name", validators=[
                            InputRequired(), Length(max=30)])


class LoginForm(FlaskForm):

    username = StringField("Username", validators=[
                           InputRequired(), Length(min=4, max=20)])

    password = PasswordField("Password", validators=[
                             InputRequired(), Length(min=8)])


class FeedbackForm(FlaskForm):

    title = StringField("Title", validators=[InputRequired(), Length(max=100)])

    content = TextAreaField("Content", validators=[InputRequired()])
