class DummyAuthException(Exception):
    """ A generic local exception. """

    def __init__(self, message, status_code=500):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code


class InvalidParameterException(DummyAuthException):
    """ Used when a parameter is not properly set. """

    def __init__(self, message):
        DummyAuthException.__init__(self, message, status_code=400)


class InvalidAuthorizationResponseException(DummyAuthException):
    """ Used when the server returns an invalid response. """

    def __init__(self, message):
        DummyAuthException.__init__(self, message, status_code=401)
