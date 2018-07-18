from flask import Flask, request, jsonify
import os
import json
from gitlab_analytics_models import *
from webhook_handler import dispatch
from flask import render_template
from flask import request

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
    mysql_host = os.getenv("MYSQL_HOST")
    mysql_port = os.getenv("MYSQL_PORT")
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    mysql_database = os.getenv("MYSQL_DATABASE")
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


@app.route("/admin", methods=['GET', 'POST'])
def admin():
    # TODO when will webhooks be added to gitlab repos?
    setup_db_connection()
    config_names = ['external_url', 'gitlab_url', 'private_token']
    if request.method == 'POST':
        if not Settings.table_exists():
            initialize_db()
        for name in config_names:
            value = request.form[name]
            s, exists = Settings.get_or_create(name=name)
            s.value = value
            s.save()

    configs = {}
    if Settings.table_exists():
        for name in config_names:
            row = Settings.get_or_none(name=name)
            if row is not None:
                configs[name] = row.value
    app.logger.debug("configs: ")
    app.logger.debug(configs)
    return render_template('admin.html', name="admin", **configs)


@app.route('/web_hook/', methods=['POST'])
def web_hook():
    try:
        ret = dispatch(request.get_json())
        return jsonify(ret)
    except:
        app.logger.error("Error Data: ")
        app.logger.error(request.get_json())
        return jsonify({'ret': -1, 'message': 'Error Input Data'})


if __name__ == '__main__':
    # init_mariadb()
    port = os.getenv("PORT")
    app.run(debug=True, host='0.0.0.0', port=port)
