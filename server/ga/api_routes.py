from flask import Blueprint
from flask import current_app as app
from flask import jsonify
from flask import redirect
from flask import request
from flask import url_for
from flask_login import login_required
from gitlab.exceptions import GitlabError
from requests.exceptions import RequestException

from .models.response_status import ResponseStatus
from .services import dbservice
from .services import gitlabservice

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
    status = ResponseStatus.OK.code
    try:
        data = {
            "status": status,
            "items": gitlabservice.get_projects_with_pagination(page=page, per_page=size),
            "totalItems": gitlabservice.get_projects_total_num()}
        return jsonify(data)
    except GitlabError as ex:
        if ex.response_code == 401:
            message = "Please make sure your gitlab access token is valid " \
                      "and have complete read/write access to the API. " + str(ex)
        else:
            message = str(ex)
        status = ResponseStatus.ERROR.code
    except RequestException as ex:
        status = ResponseStatus.ERROR.code
        message = str(ex)
    return jsonify(status=status, message=message)


@bp.route('/add_hook_to_project', methods=['POST'])
@login_required
def add_hook_to_project():
    data = request.get_json()
    project_id = data['id']

    success, message = gitlabservice.add_hook(project_id)
    if success:
        return jsonify(status=ResponseStatus.OK.code)
    else:
        return jsonify(status=ResponseStatus.ERROR.code, message=message)


@bp.route('/remove_hook_from_project', methods=['POST'])
@login_required
def remove_hook_from_project():
    data = request.get_json()
    project_id = data['id']
    success, message = gitlabservice.remove_hook(project_id)
    if success:
        return jsonify(status=ResponseStatus.OK.code)
    else:
        return jsonify(status=ResponseStatus.ERROR.code, message=message)
