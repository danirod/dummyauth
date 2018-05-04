from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL, ValidationError
from wtforms import Field, StringField
from urllib.parse import urlsplit, urlunsplit
from ipaddress import ip_address


class ValidUserProfile(object):
    """
    This validator tests for additional rules that a valid profile URL must
    comply. These rules are defined in section 3.1 of the IndieAuth spec.
    There may be something similar in the OAuth 2.0 spec, but I haven't read
    the entire spec at this moment.
    """
    def __init__(self, message=None):
        if not message:
            message = 'User profile URL is invalid.'
        self.message = message

    def __call__(self, form: FlaskForm, field: Field):
        components = urlsplit(field.data or '')

        # Scheme must be http or https.
        if not components.scheme or components.scheme not in ('http', 'https'):
            raise ValidationError(self.message)

        # Things that must not be present: username, password, fragment, port.
        if components.username or components.password or \
           components.fragment or components.port:
            raise ValidationError(self.message)

        # Must have a path.
        if not components.path:
            raise ValidationError(self.message)

        # Must not have /./ or /../ as segments in the path.
        path_segments = components.path.split('/')
        if '.' in path_segments or '..' in path_segments:
            raise ValidationError(self.message)

        # Netloc should be a hostname, not an IP address.
        try:
            ip_address(components.netloc)
        except ValueError:
            pass
        else:
            # ValidationError is a subclass of ValueError.
            # Can't raise this exception inside the try: block.
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    """
    This form validates the domain typed in by the user in the login view.
    It validates that the domain is a valid domain name, and it validates
    additional rules defined in the spec.
    """
    domain = StringField('Domain', validators=[
        DataRequired('Please, input a domain name to log in'),
        URL(message='Please, use a valid URL'),
        ValidUserProfile(message='Please, use a valid URL'),
    ])
