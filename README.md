DummyAuth
=========

A web application that allows you to log in through RelMeAuth and IndieAuth.
Doesn't do anything, but it may help during the development or debugging
process of other IndieWeb applications.


Requirements
------------

* Python 3.6 + pipenv

**In this house we use pipenv**.


How to run
----------

### Environment variables

Flask will read the environment variables from an .env file if such file
exists in the project root directory. This is handy during development.
Alternatively, use your shell to export environment variables, set them
when creating the Docker container, or use any other way to pass environment
variables to the application.

Environment variables:

* SECRET_KEY: the key to use to encrypt sessions. Please, set up a key.
* FLASK_ENV: the environment to use: "production" or "development".
* FLASK_DEBUG: whether to enable debug (FLASK_DEBUG=1) or not (FLASK_DEBUG=0).
* HOST: host to bind the application on. By default, it will bind the server
  to 0.0.0.0, listening on all interfaces, unless changed to something better
  (i.e. HOST="127.0.0.1" or HOST="192.168.1.33").


### Internal Flask server

* Install pipenv if you don't have it: `pip install pipenv` or use your
  system package manager (use the PPA, `brew install pipenv` on MacOS X...)
* `pipenv install` to install dependencies.
* `pipenv run flask run` to run the internal Flask server.


### WSGI, Gunicorn

**Under development**.


### Docker

You can build the Dockerfile included in this project and run the server using
Docker. When running inside the Docker container, the following environment
variables are set by default:

* FLASK_ENV: `production`, unless changed.
* FLASK_DEBUG: `0`, unless changed.

An usage example:

    $ docker build -t danirod/dummyauth:1.0 .
    $ docker run --rm -p 127.0.0.1:5000:5000 \
      -e SECRET_KEY="can you keep a secret?" \
      danirod/dummyauth:1.0


Current caveats
---------------

### No RelMeAuth support

Even if your homepage has rel="me" links for every social network ever created,
you won't be able to login unless you add a rel="authorization_endpoint" link
to your homepage.

As a further experiment, if the validator doesn't find an authorization_endpoint
but finds rel="me" links, it should take you to IndieLogin.com to authenticate
yourself using one of your social identities (Twitter, GitHub...)


### May accept invalid profile URLs

At the moment Dummy Auth does not validate an URL against the rules defined
in Section 3.1 of the IndieAuth spec. For instance, URLs that have a port
component or a fragment component.


### Does not accept a hostname

It would be easier if you could just use `example.com` and let the system
add http: or https:. At the moment you have to type `http://example.com/` or
the validation will fail.
