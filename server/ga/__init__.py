import os
from flask import Flask
from flask_login import LoginManager
from flask import url_for
from flask import redirect

from . import routes
from ga.components.gauser import GAUser
from .services import dbservice


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

    app.register_blueprint(routes.mod, url_prefix='/')

    # login_manager 相关代码放在这里是否合适？
    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.blueprint_login_views = {
        'ga': '/signin',
    }

    @login_manager.user_loader
    def load_user(user_id):
        return GAUser(user_id)

    with app.app_context():
        dbservice.connect()
        if not dbservice.is_initialized():
            dbservice.initialize()
        dbservice.load_settings()
    return app
