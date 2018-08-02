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

mod = Blueprint('ga', __name__, template_folder="templates",
                static_folder='static')


@mod.route('/', methods=['GET'])
def root_route():
    return redirect(url_for('.settings'))


@mod.route('/signup', methods=['GET', 'POST'])
def signup():
    if dbservice.password_exists():
        return redirect(url_for('.signin'))

    if request.method == 'POST':
        password = request.form["password"]
        dbservice.save_password(password)
        return redirect(url_for('.signin'))
    return render_template('admin/signup.html')


@mod.route('/signin', methods=['GET', 'POST'])
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


@mod.route('/signout', methods=['GET'])
def signout():
    flask_login.logout_user()
    return redirect(url_for('.signin'))


@mod.route('/settings', methods=['GET', 'POST'])
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
        d['external_url'] = request.url_root + "web_hook"
    return render_template('admin/settings.html', **d)


@mod.route('/hooks', methods=['GET'])
@login_required
def hooks():
    projects = gitlabservice.get_projects()
    return render_template('admin/hooks.html', projects=projects)


@mod.route('/add_hook_to_project', methods=['POST'])
def add_hook_to_project():
    data = request.get_json()
    project_id = data['id']
    gitlabservice.add_hook(project_id)
    # fixme need better response
    return ""


@mod.route('/remove_hook_from_project', methods=['POST'])
def remove_hook_from_project():
    data = request.get_json()
    project_id = data['id']
    gitlabservice.remove_hook(project_id)
    # fixme need better response
    return ""


@mod.route('/web_hook/', methods=['POST'])
def web_hook():
    try:
        ret = webhookservice.dispatch(request.get_json())
        return jsonify(ret)
    except:
        app.logger.error("Error Data: ")
        app.logger.error(request.get_json())
        return jsonify({'ret': -1, 'message': 'Error Input Data'})


@mod.route('/system_hook/', methods=['POST'])
def system_hook():
    try:
        ret = systemhookservice.dispatch(request.get_json())
        return jsonify(ret)
    except:
        app.logger.error("Error Data: ")
        app.logger.error(request.get_json())
        return jsonify({'ret': -1, 'message': 'Error Input Data'})
