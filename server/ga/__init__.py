import os
from flask import Flask

from . import routes
from .services import loginservice


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'this is a secret key'
    # all the env here are defined in docker-compose.yml
    app.config['mysql_host'] = os.getenv('MYSQL_HOST', '127.0.0.1')
    app.config['mysql_port'] = os.getenv('MYSQL_PORT', 3306)
    app.config['mysql_user'] = os.getenv('MYSQL_USER', 'ga')
    app.config['mysql_password'] = os.getenv('MYSQL_PASSWORD', '4t9wegcvbYSd')
    app.config['mysql_database'] = os.getenv('MYSQL_DATABASE',
                                             'gitlab_analytics')
    app.register_blueprint(routes.bp, url_prefix='/')
    loginservice.init_app(app, {'ga': '/signin'})
    return app
