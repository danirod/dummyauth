from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL
from wtforms import StringField

class LoginForm(FlaskForm):
    """
    This form validates the domain typed in by the user in the login view.
    It validates that the domain is a valid domain name, and it validates
    additional rules defined in the spec.
    """
    domain = StringField('Domain', validators=[
        DataRequired('Please, input a domain name to log in'),
        URL(message='Please, use a valid URL'),
    ])
