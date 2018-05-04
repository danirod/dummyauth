import requests
from dummyauth.exceptions import InvalidAuthorizationResponseException
from urllib.parse import parse_qs, urljoin
from bs4 import BeautifulSoup


class AuthorizationCodeValidator(object):

    def __init__(self, authorization_endpoint: str, code: str,
                 client_id: str, redirect_uri: str):
        self.__authorization_endpoint = authorization_endpoint
        self.__code = code
        self.__client_id = client_id
        self.__redirect_uri = redirect_uri
        self.__fetched = False
        self.__valid = False
        self.__me = None
        self.__error = None

    @classmethod
    def __parse_response(cls, request):
        content_type = request.headers['content-type']
        if content_type == 'application/json':
            return request.json()
        elif content_type == 'application/x-www-form-urlencoded':
            qs = parse_qs(request.text)
            return {k: qs[k][0] for k in qs }
        else:
            message = 'Unsupported content-type: {}'.format(content_type)
            raise InvalidAuthorizationResponseException(message)

    def __fetch(self):
        """ Perform validation. """
        payload = {
            'code': self.__code,
            'client_id': self.__client_id,
            'redirect_uri': self.__redirect_uri
        }
        request = requests.post(self.__authorization_endpoint, data=payload)
        self.__fetched = True
        if request.status_code == 200:
            self.__valid = True
            response = self.__parse_response(request)
            if 'me' in response:
                self.__me = response['me']
            else:
                self.__valid = False
                self.__error = 'invalid_payload'
        else:
            self.__valid = False
            response = self.__parse_response(request)
            self.__error = response.get('error', '')

    @property
    def valid(self) -> bool:
        """ Will return True if the validation request was successful. """
        if not self.__fetched:
            self.__fetch()
        return self.__valid

    @property
    def profile_url(self) -> str:
        """ In case the request is valid, will hold the canonical URL. """
        if not self.__fetched:
            self.__fetch()
        return self.__me

    @property
    def error(self) -> str:
        """ In case the request is not valid, will hold the response error. """
        if not self.__fetched:
            self.__fetch()
        return self.__error


class EndpointDiscoverySpider(object):
    """
    This class is responsible for fetching the given online identity by the
    user looking for an authorization_endpoint link either in the HTTP headers
    of the returned web document, or in the HTML content of the web page.

    Discovery is done in conformance to section 4.1 of the IndieAuth protocol.
    Therefore, the following statements are true about the behaviour of this
    discovery spider:

    * An HTTP head request will be made beforehand looking for a Link header
      with the proper rel value of authorization_endpoint. Only if such link
      is not found as an HTTP header, a GET request will be sent to the same
      URL.

    * The spider will also follow redirects up to a limit of 5 redirections.
      If such limit is reached, an exception will be raised to alert the user
      that there were too many redirects in this webpage.

    * The target URL of a redirect is also noted to generate the canonical
      URL of the person. The behaviour of the spider depends on the actual
      HTTP status code given by the page. An HTTP 301 or HTTP 308 will change
      the canonical URL. An HTTP 302 or HTTP 307 will keep the current URL as
      the canonical URL. Both cases will change the discovery URL anyway.
    """

    def __init__(self, discovery_url: str, redirection_limit: int=5):
        """ Initialize the discovery spider.

        This method won't perform any actual HTTP request. This has to be
        commanded using one of the methods or properties that triggers an HTTP
        request.

        :param discovery_url: the URL to execute discovery on. Endpoint links
            will be found at the given URL unless redirections change it.
        :param redirection_limit: the maximum number of redirections that
            the spider will follow before givin up. If the discovery URL
            returns an HTTP 301, 302, 307 or 308 status code, a new HTTP
            request will be done unless it has happened as many times as
            the value of this variable. In such case, an exception will be
            raised.
        """

        # Parameters used during the fetching phase.
        self.__discovery_url = discovery_url
        self.__redirect_limit = redirection_limit

        # Parameters set after fetching the data.
        self.__canonical_url = None
        self.__target_url = None
        self.__authorization_endpoint = None
        self.__token_endpoint = None
        self.__fetched = False

    @property
    def fetched(self) -> bool:
        """ Returns true if the endpoint has already been discovered. """
        return self.__fetched

    @property
    def canonical_url(self) -> str:
        """ Returns the canonical URL of the user. """
        if not self.__fetched:
            self.__fetch()
        return self.__canonical_url

    @property
    def target_url(self) -> str:
        """ Returns the URL where the data was finally fetched from. """
        if not self.__fetched:
            self.__fetch()
        return self.__target_url

    @property
    def authorization_endpoint(self) -> str:
        """ Returns the authorization endpoint of the user. """
        if not self.__fetched:
            self.__fetch()
        return self.__authorization_endpoint

    @property
    def token_endpoint(self) -> str:
        """ Returns the token endpoint of the user. """
        if not self.__fetched:
            self.__fetch()
        return self.__token_endpoint

    def __fetch(self):
        """ Discover the endpoints for this URL. """
        fields = self.__discover(self.__discovery_url, self.__redirect_limit)
        self.__canonical_url = fields['canonical_url']
        self.__target_url = fields['discovery_url']
        self.__authorization_endpoint = fields['authorization_endpoint']
        self.__token_endpoint = fields['token_endpoint']
        self.__fetched = True

    @classmethod
    def __discover(self, discovery_url: str, max_redirects: int=5) -> dict:
        """ Send an HTTP request to discover the endpoints for this URL. """
        request = requests.head(discovery_url, allow_redirects=False)

        # Redirections have to be followed.
        if request.status_code in (301, 302, 307, 308):
            # Maybe we've gone too deep?
            if not max_redirects > 0:
                raise ValueError('Too many redirects.')

            # Build the new discovery URL. Note we use urljoin because the
            # location header may be a relative URL. Use the discovery URL
            # to build the final value.
            target_url = urljoin(discovery_url, request.headers['location'])

            # Send a new request recursively.
            new_discovery = self.__discover(target_url, max_redirects - 1)
            if request.status_code in (302, 307):
                # Not a permanent redirection: keep the canonical URL.
                new_discovery['canonical_url'] = discovery_url
            return new_discovery

        # This is the response object that will be returned to the user.
        data = {
            'canonical_url': discovery_url,
            'discovery_url': discovery_url,
            'authorization_endpoint': None,
            'token_endpoint': None
        }

        # Find for a valid authorization_endpoint in the URL.
        if 'authorization_endpoint' in request.links:
            auth_endpoint = request.links['authorization_endpoint']['url']
            absolute_auth_endpoint = urljoin(discovery_url, auth_endpoint)
            data['authorization_endpoint'] = absolute_auth_endpoint

        # Find for a valid token_endpoint in the URL.
        if 'token_endpoint' in request.links:
            token_endpoint = request.links['token_endpoint']['url']
            absolute_token_endpoint = urljoin(discovery_url, token_endpoint)
            data['token_endpoint'] = absolute_token_endpoint

        if not data['authorization_endpoint'] or not data['token_endpoint']:
            # We'll have to parse the contents of the document anyway.
            # HEAD and GET status code and headers must be the same, so
            # we don't have to do this circus again.
            request = requests.get(discovery_url, stream=True)

            # Note we have set streaming mode to avoid fetching large items.
            content = b''
            for chunk in request.iter_content(1024):
                content += chunk
                if len(content) >= 1024 * 1024:
                    chunk.close()
                    break

            soup = BeautifulSoup(content, 'html5lib')

            # Seek for an authorization endpoint.
            tag = soup.find('link', rel='authorization_endpoint')
            if tag and not data['authorization_endpoint']:
                endpoint = urljoin(discovery_url, tag['href'])
                data['authorization_endpoint'] = endpoint

            # Seek for a token endpoint
            tag = soup.find('link', rel='token_endpoint')
            if tag and not data['token_endpoint']:
                endpoint = urljoin(discovery_url, tag['href'])
                data['token_endpoint'] = endpoint

        return data
