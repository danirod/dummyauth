import httpretty
import sure
from dummyauth.spider import AuthorizationCodeValidator
from unittest import TestCase

class AuthorizationCodeValidatorTestCase(TestCase):

    @httpretty.httprettified
    def test_spider_handles_valid_requests(self):
        httpretty.register_uri(httpretty.POST, 'http://auth.example.com/login',
                               adding_headers={'content-type': 'application/json'},
                               body='{"me": "http://johndoe.example.com/"}')
        validator_params={
            'authorization_endpoint': 'http://auth.example.com/login',
            'code': 'deadbeef',
            'client_id': 'http://client.example.com/',
            'redirect_uri': 'http://client.example.com/callback',
        }
        validator = AuthorizationCodeValidator(**validator_params)
        self.assertTrue(validator.valid)

    @httpretty.httprettified
    def test_spider_handles_valid_profile_url(self):
        httpretty.register_uri(httpretty.POST, 'http://auth.example.com/login',
                               adding_headers={'content-type': 'application/json'},
                               body='{"me": "http://johndoe.example.com/"}')
        validator_params={
            'authorization_endpoint': 'http://auth.example.com/login',
            'code': 'deadbeef',
            'client_id': 'http://client.example.com/',
            'redirect_uri': 'http://client.example.com/callback',
        }
        validator = AuthorizationCodeValidator(**validator_params)
        validator.profile_url.should.equal('http://johndoe.example.com/')

    @httpretty.httprettified
    def test_spider_handles_invalid_requests(self):
        httpretty.register_uri(httpretty.POST, 'http://auth.example.com/login',
                               adding_headers={'content-type': 'application/json'},
                               body='{"error": "invalid_request"}',
                               status=400)
        validator_params={
            'authorization_endpoint': 'http://auth.example.com/login',
            'code': 'deadbeef',
            'client_id': 'http://client.example.com/',
            'redirect_uri': 'http://client.example.com/callback',
        }
        validator = AuthorizationCodeValidator(**validator_params)
        self.assertFalse(validator.valid)

    @httpretty.httprettified
    def test_spider_handles_invalid_request_code(self):
        httpretty.register_uri(httpretty.POST, 'http://auth.example.com/login',
                               adding_headers={'content-type': 'application/json'},
                               body='{"error": "invalid_request"}',
                               status=400)
        validator_params={
            'authorization_endpoint': 'http://auth.example.com/login',
            'code': 'deadbeef',
            'client_id': 'http://client.example.com/',
            'redirect_uri': 'http://client.example.com/callback',
        }
        validator = AuthorizationCodeValidator(**validator_params)
        validator.error.should.equal('invalid_request')

    @httpretty.httprettified
    def test_spider_sends_appropiate_request(self):
        httpretty.register_uri(httpretty.POST, 'http://auth.example.com/login',
                               adding_headers={'content-type': 'application/json'},
                               body='{"me": "http://johndoe.example.com/"}')
        validator_params={
            'authorization_endpoint': 'http://auth.example.com/login',
            'code': 'deadbeef',
            'client_id': 'http://client.example.com/',
            'redirect_uri': 'http://client.example.com/callback',
        }
        AuthorizationCodeValidator(**validator_params).valid
        httpretty.has_request().should.be(True)

    @httpretty.httprettified
    def test_spider_sends_appropiate_code(self):
        httpretty.register_uri(httpretty.POST, 'http://auth.example.com/login',
                               adding_headers={'content-type': 'application/json'},
                               body='{"me": "http://johndoe.example.com/"}')
        validator_params={
            'authorization_endpoint': 'http://auth.example.com/login',
            'code': 'deadbeef',
            'client_id': 'http://client.example.com/',
            'redirect_uri': 'http://client.example.com/callback',
        }
        AuthorizationCodeValidator(**validator_params).valid
        payload = httpretty.last_request().parsed_body
        payload['code'][0].should.equal('deadbeef')

    @httpretty.httprettified
    def test_spider_sends_appropiate_client_id(self):
        httpretty.register_uri(httpretty.POST, 'http://auth.example.com/login',
                               adding_headers={'content-type': 'application/json'},
                               body='{"me": "http://johndoe.example.com/"}')
        validator_params={
            'authorization_endpoint': 'http://auth.example.com/login',
            'code': 'deadbeef',
            'client_id': 'http://client.example.com/',
            'redirect_uri': 'http://client.example.com/callback',
        }
        AuthorizationCodeValidator(**validator_params).valid
        payload = httpretty.last_request().parsed_body
        payload['client_id'][0].should.equal('http://client.example.com/')

    @httpretty.httprettified
    def test_spider_sends_appropiate_redirect_uri(self):
        httpretty.register_uri(httpretty.POST, 'http://auth.example.com/login',
                               adding_headers={'content-type': 'application/json'},
                               body='{"me": "http://johndoe.example.com/"}')
        validator_params={
            'authorization_endpoint': 'http://auth.example.com/login',
            'code': 'deadbeef',
            'client_id': 'http://client.example.com/',
            'redirect_uri': 'http://client.example.com/callback',
        }
        AuthorizationCodeValidator(**validator_params).valid
        payload = httpretty.last_request().parsed_body
        payload['redirect_uri'][0].should.equal('http://client.example.com/callback')
