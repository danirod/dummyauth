DummyAuth
=========

A web application that allows you to log in through RelMeAuth and IndieAuth.
Doesn't do anything, but it may help during the development or debugging
process of other IndieWeb applications.


Requirements
------------

* Python 3.6. (May work on Python 3.5, but it hasn't been tested)
* **In this house we use pipenv**. Get it using `pip install pipenv`.


How to run
----------

### Development mode

This application uses the Flask application pattern factory, so importing
the `dummyauth` module will expose a `create_app` function. There is also an
uwsgi.py that exposes an app object.

During development mode you'll probably use Flask internal development server.
This server is designed to be used during development and it's not suitable
for the safety and performance standards used in production environments.
However, it's easy to use and it can be used in development mode.

Make sure you've installed Pipfile dependencies using:

    pipenv install

Because of how Python works, the dummyauth package needs to be in your
PYTHONPATH. Either add the project root to your PYTHONPATH, or simply install
this package in development mode:

    pipenv shell
    pip install -e .

Then you can proceed to run the application:

    flask run

The application will run in production mode by default. You may want to change
to development mode during development in order to have things such as
reloading or a predefined secret key.

    FLASK_ENV=development flask run

**No secret key has been set by default in production mode**. See below for
more information on how to set a secret key using environment variables.

**Environment variables**: If an .env file is found in the project root
directory, those variables will be read and used in the Flask server. There
are a few useful environment variables.

* SECRET_KEY: The key to use to encrypt session. Please, use a key.
* FLASK_ENV: The environment to run the server in: production, development...
* FLASK_DEBUG: Whether to enable debug (FLASK_DEBUG=1) or not (FLASK_DEBUG=0).


### WSGI application server

The WSGI server increases the performance of the Flask application and it's
what you should use to run your application in a production server. You're
encouraged to still put a web server on top of your application server and
to reverse proxy requests to your application server, such as using NGINX or
Apache.

Suggested application servers are uWSGI and Gunicorn. None of them are in the
Pipfile.

In both cases, you can use `wsgi:app` as the module to load inside your WSGI
server. This is an application instance ready to be used by your WSGI server.
Depending on which server you choose, you'll have to pass this module using
a different method.


### Docker images

You can build the Dockerfile included in this project and run the server using
Docker. The Docker image will use the uWSGI application server and expose it
in port 5000. You may want to put this port behind a reverse proxy web server
such as NGINX.

You still have to set the secret key using the SECRET_KEY environment variable.
A full example on how to build and deploy this image using Docker:

    $ docker build -t dummyauth:1.0 .
    $ docker run --rm -p 5000:5000 -e SECRET_KEY="s3cr3t" dummyauth:1.0


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
