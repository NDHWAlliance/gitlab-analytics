from flask import current_app as app

from ga.components.gauser import GAUser
from . import dbservice
from flask_login import login_user


def login(password):
    if not dbservice.check_password(password):
        app.logger.warning('invalid password: ' + password)
        return False
    user = GAUser('admin')
    login_user(user)
    return True
