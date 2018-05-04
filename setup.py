from setuptools import setup

setup(
    name = "dummyauth",
    version = "1.0.1",
    author = "Dani Rodríguez",
    author_email = "dani@danirod.es",
    description = ("An IndieWeb app to test your authorization endpoint"),
    license = "ISC",
    keywords = "indieauth indieweb login",
    url = "https://github.com/danirod/dummyauth",
    packages=['dummyauth', 'test'],
)
