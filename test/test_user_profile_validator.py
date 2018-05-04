from unittest import TestCase
from unittest.mock import patch, Mock
from dummyauth.forms import ValidUserProfile
from wtforms.validators import ValidationError

@patch('flask_wtf.FlaskForm', autospec=True)
class LoginFormTestCase(TestCase):

    def test_validator_accepts_url(self, form):
        field = Mock(data='https://example.com/')
        ValidUserProfile()(form, field)

    def test_validator_accepts_url_with_path(self, form):
        field = Mock(data='https://example.com/username')
        ValidUserProfile()(form, field)

    def test_validator_accepts_url_with_querystring(self, form):
        field = Mock(data='https://example.com/users?id=100')
        ValidUserProfile()(form, field)

    def test_validator_rejects_url_without_scheme(self, form):
        field = Mock(data='example.com')
        self.assertRaises(ValidationError, ValidUserProfile(), form, field)

    def test_validator_rejects_url_with_invalid_scheme(self, form):
        field = Mock(data='mailto:user@example.com')
        self.assertRaises(ValidationError, ValidUserProfile(), form, field)

    def test_validator_rejects_url_with_dot_path_segment(self, form):
        field = Mock(data='https://example.com/foo/./bar')
        self.assertRaises(ValidationError, ValidUserProfile(), form, field)

    def test_validator_rejects_url_with_double_dot_path_segment(self, form):
        field = Mock(data='https://example.com/foo/../bar')
        self.assertRaises(ValidationError, ValidUserProfile(), form, field)

    def test_validator_rejects_url_with_a_fragment(self, form):
        field = Mock(data='https://example.com/#me')
        self.assertRaises(ValidationError, ValidUserProfile(), form, field)

    def test_validator_rejects_url_with_username_and_password(self, form):
        field = Mock(data='https://user:pass@example.com/')
        self.assertRaises(ValidationError, ValidUserProfile(), form, field)

    def test_validator_rejects_url_with_port(self, form):
        field = Mock(data='https://example.com:8443/')
        self.assertRaises(ValidationError, ValidUserProfile(), form, field)

    def test_validator_rejects_url_with_ip_address(self, form):
        field = Mock(data='https://172.28.92.51/')
        self.assertRaises(ValidationError, ValidUserProfile(), form, field)
