import os
import logging
from flask import Flask

from . import routes
from . import api_routes
from .services import loginservice
from . import commands


def create_app():
    logging.basicConfig(level=logging.DEBUG, datefmt='%Y-%m-%d:%H:%M:%S',
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

    logging.getLogger("peewee").setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.DEBUG)
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'this is a secret key'
    # all the env here are defined in docker-compose.yml
    app.config['mongo_host'] = os.getenv('MONGO_HOST', '127.0.0.1')
    app.config['mongo_port'] = os.getenv('MONGO_PORT', 27017)
    app.config['mongo_username'] = os.getenv('MONGO_USERNAME', 'ga')
    app.config['mongo_password'] = os.getenv('MONGO_PASSWORD', '4t9wegcvbYSd')
    app.config['mongo_database'] = os.getenv('MONGO_DATABASE', 'gitlab_analytics')
    # default is False
    app.config['mongo_available'] = os.getenv('MONGO_AVAILABLE', "FALSE") == "TRUE"

    app.config['mysql_host'] = os.getenv('MYSQL_HOST', '127.0.0.1')
    app.config['mysql_port'] = os.getenv('MYSQL_PORT', 3306)
    app.config['mysql_user'] = os.getenv('MYSQL_USER', 'ga')
    app.config['mysql_password'] = os.getenv('MYSQL_PASSWORD', '4t9wegcvbYSd')
    app.config['mysql_database'] = os.getenv('MYSQL_DATABASE',
                                             'gitlab_analytics')
    app.register_blueprint(routes.bp, url_prefix='/')
    loginservice.init_app(app, {'ga_page': '/signin'})
    app.register_blueprint(api_routes.bp, url_prefix='/api')
    commands.init_commands(app)
    return app
