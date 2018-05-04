from flask import Flask
from flask_wtf import CSRFProtect
from dummyauth import views
from dummyauth.exceptions import DummyAuthException
import os

csrf = CSRFProtect()

def create_app():
    configs = {
        'production': 'dummyauth.config.BaseConfig',
        'development': 'dummyauth.config.DevelopmentConfig',
        'testing': 'dummyauth.config.TestingConfig',
    }
    app = Flask(__name__)
    app.config.from_object(configs.get(app.env, configs['production']))
    csrf.init_app(app)

    app.add_url_rule('/', 'login', views.login_view, methods=['GET', 'POST'])
    app.add_url_rule('/callback', 'callback', views.login_callback)
    app.add_url_rule('/success', 'success', views.display_profile)
    app.add_url_rule('/error', 'failure', views.handle_error_response)
    app.add_url_rule('/logout', 'logout', views.clear_session, methods=['POST'])

    # Register an error handler for exceptions.
    app.register_error_handler(DummyAuthException, views.handle_error_response)
    return app

__all__ = ['create_app']
