from flask import Flask, jsonify
import os
from gitlab_analytics_models import *
import webhook_handler
import system_hook_handler
from flask import render_template, redirect
from flask import request
from ga_config import ga_config
import gitlab_api

app = Flask(__name__)


@app.route("/", methods=['GET'])
def root():
    initialize_ga_config()

    if not ga_config['external_url']:
        ga_config['external_url'] = '{}web_hook/'.format(request.base_url)

    return render_template('admin.html', name="admin", **ga_config)


def setup_db_connection():
    # all the env here are defined in docker-compose.yml
    mysql_host = os.getenv('MYSQL_HOST', '127.0.0.1')
    mysql_port = os.getenv('MYSQL_PORT', 3306)
    mysql_user = os.getenv('MYSQL_USER', 'ga')
    mysql_password = os.getenv('MYSQL_PASSWORD', '4t9wegcvbYSd')
    mysql_database = os.getenv('MYSQL_DATABASE', 'gitlab_analytics')
    app.logger.debug(
        "setup db connection {}@{}:{}".format(mysql_user, mysql_host,
                                              mysql_database))

    database.database = mysql_database
    database.connect_params = {'host': mysql_host, 'port': int(mysql_port),
                               'user': mysql_user,
                               'password': str(mysql_password),
                               'charset': 'utf8', 'use_unicode': True}


def initialize_db():
    app.logger.info("initialize_db")
    database.execute_sql(
        'alter database gitlab_analytics default character set utf8 collate utf8_general_ci')
    database.create_tables([GitlabCommits, GitlabIssues, GitlabWikiCreate,
                            GitlabWikiUpdate, GitlabIssueComment,
                            GitlabMergeRequest, GitlabMRAssigneeComment,
                            GitlabMRInitiatorComment, Settings])


def initialize_ga_config():
    setup_db_connection()
    if not Settings.table_exists():
        return

    for name in ga_config.keys():
        row = Settings.get_or_none(name=name)
        if row is not None:
            ga_config[name] = row.value


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    setup_db_connection()
    if request.method == 'POST':
        if not Settings.table_exists():
            initialize_db()
        for name in ga_config.keys():
            value = request.form[name]
            s, exists = Settings.get_or_create(name=name)
            s.value = value
            s.save()
        initialize_ga_config()
        return redirect('add_hook')

    return render_template('admin.html', name="admin", **ga_config)


@app.route('/add_hook/', methods=['GET'])
def add_hook():
    # get projects with private_token
    projects = []
    for project in gitlab_api.list_all_projects():

        if webhook_handler.is_hooked(project.id, ga_config['external_url']):
            hooked = 1
        else:
            hooked = 0

        projects.append({
            "id": project.id,
            "url": project.web_url,
            "hooked": hooked,
            "loading": 0

        })

    app.logger.debug("projects: ")
    app.logger.error(len(projects))

    return render_template('addhook2.html', hook=ga_config['external_url'],
                           projects=projects, **ga_config)


@app.route('/add_hook_to_project', methods=['POST'])
def add_hook_to_project():
    data = request.get_json()
    project_id = data['id']
    webhook_handler.add_hook(project_id, ga_config['external_url'])
    # fixme need better response
    return ""


@app.route('/remove_hook_from_project', methods=['POST'])
def remove_hook_from_project():
    data = request.get_json()
    project_id = data['id']
    gitlab_api.remove_hook(project_id, ga_config['external_url'])
    # fixme need better response
    return ""


@app.route('/web_hook/', methods=['POST'])
def web_hook():
    try:
        ret = webhook_handler.dispatch(request.get_json())
        return jsonify(ret)
    except:
        app.logger.error("Error Data: ")
        app.logger.error(request.get_json())
        return jsonify({'ret': -1, 'message': 'Error Input Data'})


@app.route('/system_hook/', methods=['POST'])
def system_hook():
    try:
        ret = system_hook_handler.dispatch(request.get_json())
        return jsonify(ret)
    except:
        app.logger.error("Error Data: ")
        app.logger.error(request.get_json())
        return jsonify({'ret': -1, 'message': 'Error Input Data'})


if __name__ == '__main__':
    # init_mariadb()
    port = os.getenv("PORT")
    initialize_ga_config()
    app.run(debug=True, host='0.0.0.0', port=port)
