DummyAuth
=========

A web application that allows you to log in through RelMeAuth and IndieAuth.
Doesn't do anything, but it may help during the development or debugging
process of other IndieWeb applications.


Requirements
------------

* Python 3.6 + pipenv

**In this house we use pipenv**.


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
