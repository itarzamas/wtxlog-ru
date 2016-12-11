# -*- coding: utf-8 -*-

from flask import Blueprint

myapi = Blueprint('myapi', __name__)

from . import views
from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import Email, DataRequired, EqualTo

class LoginForm(Form):
    email = StringField('E-mail', validators=[Email(), DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])

class RegistrationForm(LoginForm):
    password_repeat = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
