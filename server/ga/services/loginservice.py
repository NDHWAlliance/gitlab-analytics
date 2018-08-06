from flask_login import LoginManager
from ..components.gauser import GAUser


def init_app(app, blueprint_login_views={}):
    # login_manager 相关代码放在这里是否合适？
    login_manager = LoginManager()
    login_manager.init_app(app)

    login_manager.blueprint_login_views = blueprint_login_views

    @login_manager.user_loader
    def load_user(user_id):
        return GAUser(user_id)
