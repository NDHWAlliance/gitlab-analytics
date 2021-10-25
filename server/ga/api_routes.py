import flask
import flask_login
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import current_app as app
from flask import jsonify
from flask_login import login_required
from flask_login import current_user
from .services import dbservice
from .services import adminservice
from .services import gitlabservice
from .services import systemhookservice
from .services import webhookservice

bp = Blueprint('ga_api', __name__, template_folder="templates",
               static_folder='static')


@bp.before_request
def load_settings_from_db():
    app.logger.info("load_settings_from_db " + request.endpoint)
    if request.endpoint in ['ga.setup', 'ga.get_db_status']:
        return
    connected, message = dbservice.connect()
    if not connected:
        # 在 setup 页面，轮询 get_db_status，等待mysql连接成功
        return redirect(url_for('.setup'))
    if not dbservice.is_initialized():
        dbservice.initialize()
    dbservice.load_settings()


@bp.route('/projects/list', methods=['GET'])
@login_required
def projects_list():
    app.logger.info(app.config)
    page = request.args.get('page')
    size = request.args.get('size')
    data = {"items": gitlabservice.get_projects_with_pagination(page=page, per_page=size),
            "totalItems": gitlabservice.get_projects_total_num()}
    return jsonify(data)


@bp.route('/projects/total_num', methods=['GET'])
@login_required
def projects_total_num():
    app.logger.info(app.config)
    num = gitlabservice.get_projects_total_num()
    return jsonify(s=0, total_num=num)
