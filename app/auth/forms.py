from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, Required
from app.models import User, Role


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField()
    submit = SubmitField()
