from flask import Flask, jsonify
import os
from gitlab_analytics_models import *
import webhook_handler
from flask import render_template, redirect
from flask import request
from ga_config import ga_config
import gitlab_api

app = Flask(__name__)


@app.route("/", methods=['GET'])
def root():
    # TODO read config values from DB
    gitlab_url = ""
    private_token = ""
    return render_template('admin.html', name="admin", gitlab_url=gitlab_url,
                           private_token=private_token)


def setup_db_connection():
    # all the env here are defined in docker-compose.yml
    mysql_host = os.getenv('MYSQL_HOST','127.0.0.1')
    mysql_port = os.getenv('MYSQL_PORT',3306)
    mysql_user = os.getenv('MYSQL_USER','ga')
    mysql_password = os.getenv('MYSQL_PASSWORD','4t9wegcvbYSd')
    mysql_database = os.getenv('MYSQL_DATABASE','gitlab_analytics')
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


@app.route('/add_hook/', methods=['GET', 'POST'])
def add_hook():
    if request.method == 'POST':
        ids = request.form['project_ids']
        webhook_handler.add_hook(project_ids=ids, web_hook=ga_config['external_url'])

    # get projects with private_token
    projects = []
    for project in gitlab_api.list_all_projects():
        hooked = False

        for hook in gitlab_api.list_hooks(project.id):
            if hook.url == ga_config['external_url']:
                hooked = True

        projects.append("id:{}, web_url:{} hooked: {}".format(project.id, project.web_url, hooked))

    app.logger.debug("configs: ")
    app.logger.debug(ga_config)

    return render_template('addhook.html', hook=ga_config['external_url'], projects=projects, **ga_config)


@app.route('/web_hook/', methods=['POST'])
def web_hook():
    try:
        ret = webhook_handler.dispatch(request.get_json())
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
