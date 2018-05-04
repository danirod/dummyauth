import os


class BaseConfig(object):
    pass
    SECRET_KEY = os.environ.get('SECRET_KEY')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY', '57eb82b5a0e36e3a')


class TestingConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = os.environ.get('SECRET_KEY', '33f1eea15f935fa0')
