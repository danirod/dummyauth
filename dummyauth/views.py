import time
from flask import redirect, render_template, request, session, url_for
from flask.views import View
from dummyauth import exceptions
from dummyauth.forms import LoginForm
from dummyauth.spider import AuthorizationCodeValidator, EndpointDiscoverySpider
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

def __update_qs(url: str, args: dict) -> str:
    """ Modifies the querystring of the given URL adding new parameters. """
    scheme, netloc, path, qs, fragment = urlsplit(url)
    querystring = parse_qs(qs)
    querystring.update(args)
    qs = urlencode(querystring)
    return urlunsplit((scheme, netloc, path, qs, fragment))

def login_view():
    """ Asks the user for a domain to sign in with. """
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # Fetch the authorization endpoint for this user.
        spider = EndpointDiscoverySpider(form.domain.data)
        if spider.authorization_endpoint:
            # The site has declared an explicit authorization endpoint.
            login_endpoint = spider.authorization_endpoint
        elif spider.supports_relmeauth():
            # The site has not declared an authorization endpoint but has
            # rel="me" links. We can let a third party authorization provider
            # handle the login process.
            login_endpoint = 'https://indieauth.com/auth'
        else:
            form.domain.errors.append('No authorization links found here')
            return render_template('welcome.html', form=form)

        # An authorization endpoint was found. Prepare the request.
        request_payload = {
            'me': spider.canonical_url,
            'client_id': url_for('login', _external=True),
            'redirect_uri': url_for('callback', _external=True),
            'state': int(time.time()),
            'response_type': 'id'
        }

        # Some data will have to be verified later on. Save using session.
        session['login.endpoint'] = login_endpoint
        session['login.state'] = request_payload['state']

        # Build the login URL and send the user there.
        login_url = __update_qs(login_endpoint, request_payload)
        return redirect(login_url), 302

    # Catch-all when nothing of the above worked.
    return render_template('welcome.html', form=form)

def login_callback():
    """ Called as a callback after login, validates the received code. """
    for session_param in ('login.endpoint', 'login.state'):
        if session_param not in session:
            error = 'Missing session key: {}'.format(session_param)
            raise exceptions.InvalidParameterException(error)

    # DummyAuth provided an state paramater. Validate it's correct.
    if int(request.args['state']) != session['login.state']:
        error = 'The given CSRF state mismatches the sent CSRF state.'
        raise exceptions.InvalidAuthorizationResponseException(error)

    # Build a validator using the required parameters.
    validator_params = {
        'authorization_endpoint': session['login.endpoint'],
        'code': request.args['code'],
        'client_id': url_for('login', _external=True),
        'redirect_uri': url_for('callback', _external=True)
    }
    validator = AuthorizationCodeValidator(**validator_params)

    # Check the authenticity of the code.
    if validator.valid:
        # Clear session data to inhabilitate repetition attacks.
        session['login.endpoint'] = session['login.state'] = None
        session['login.profile'] = validator.profile_url
        return redirect(url_for('success')), 302
    else:
        session['login.error'] = 'validation_error'
        session['login.message'] = validator.error
        return redirect(url_for('failure')), 302

def handle_error_response(exception: exceptions.DummyAuthException=None):
    """ Handles an error response. """
    if exception:
        error = 'exception'
        message = exception.message
    else:
        error = session.get('login.error', 'generic_error')
        if error == 'validation_error':
            message = session.get('login.message')
    return render_template('failure.html', errror=error, message=message)

def display_profile():
    """ If the user is logged in, it will display the profile URL. """
    profile = session.get('login.profile', None)
    if profile:
        return render_template('success.html', profile=profile)
    else:
        return redirect(url_for('login')), 302

def clear_session():
    """ Clear user data and redirect to the login view. """
    session.clear()
    return redirect(url_for('login')), 302
