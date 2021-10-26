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
from .models.response_status import ResponseStatus

bp = Blueprint('ga_page', __name__, template_folder="templates",
               static_folder='static')


@bp.before_request
def load_settings_from_db():
    app.logger.info("load_settings_from_db " + request.endpoint)

    if request.endpoint in [bp.name + '.setup', bp.name + '.get_db_status']:
        return
    connected, message = dbservice.connect()
    if not connected:
        # 在 setup 页面，轮询 get_db_status，等待mysql连接成功
        return redirect(url_for('.setup'))
    if not dbservice.is_initialized():
        dbservice.initialize()
    dbservice.load_settings()


@bp.route('/', methods=['GET'])
def root_route():
    return redirect(url_for('.settings'))


@bp.route('/setup', methods=['GET', 'POST'])
def setup():
    app.logger.info(app.config)
    s = "{mysql_user}@{mysql_host}:{mysql_port}/{mysql_database}".format(
        **app.config)
    return render_template('admin/setup.html', connection_string=s)


@bp.route('/get_db_status', methods=['GET'])
def get_db_status():
    connected, message = dbservice.connect()
    return jsonify({"connected": connected, "message": message})


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if dbservice.password_exists():
        return redirect(url_for('.signin'))

    if request.method == 'POST':
        password = request.form["password"]
        dbservice.save_password(password)
        return redirect(url_for('.signin'))
    return render_template('admin/signup.html')


@bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        password = request.form["password"]
        if not adminservice.login(password):
            return redirect(url_for('.signin'))
        next_url = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        #    return flask.abort(400)
        return redirect(next_url or url_for('.settings'))

    if not dbservice.password_exists():
        app.logger.debug("password not exists")
        return redirect(url_for('.signup'))
    if current_user.is_authenticated:
        app.logger.debug("user already logined")
        return redirect(url_for('.settings'))
    return render_template('admin/signin.html')


@bp.route('/signout', methods=['GET'])
def signout():
    flask_login.logout_user()
    return redirect(url_for('.signin'))


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        d = {}
        for name in dbservice.setting_keys:
            value = request.form[name]
            d[name] = value
        dbservice.save_settings(d)
        # return redirect(url_for('.settings'))
        return redirect(url_for('.hooks'))
    d = {}
    for name in dbservice.setting_keys:
        d[name] = app.config[name]
    if len(d['external_url']) == 0:
        d['external_url'] = request.url_root + "web_hook/"
    return render_template('admin/settings.html', **d)


@bp.route('/hooks', methods=['GET'])
@login_required
def hooks():
    projects = []
    return render_template('admin/hooks.html', projects=list(projects))




@bp.route('/web_hook', methods=['POST'])
@bp.route('/web_hook/', methods=['POST'])
def web_hook():
    try:
        ret = webhookservice.dispatch(request.get_json())
        return jsonify(ret)
    except:
        app.logger.error("Error Data: ")
        app.logger.error(request.get_json())
        return jsonify({'ret': -1, 'message': 'Error Input Data'})


@bp.route('/system_hook', methods=['POST'])
@bp.route('/system_hook/', methods=['POST'])
def system_hook():
    try:
        ret = systemhookservice.dispatch(request.get_json())
        return jsonify(ret)
    except:
        app.logger.error("Error Data: ")
        app.logger.error(request.get_json())
        return jsonify({'ret': -1, 'message': 'Error Input Data'})
