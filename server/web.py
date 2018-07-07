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
    gitlab_url = ""
    private_token = ""
    if request.method == 'POST':
        if not GitlabCommits.table_exists():
            initialize_db()
        gitlab_url = request.form['gitlab_url']
        private_token = request.form['private_token']
        s, exists = Settings.get_or_create(name="gitlab_url")
        s.value = gitlab_url
        s.save()
        s, exists = Settings.get_or_create(name="private_token")
        s.value = private_token
        s.save()

    else:
        if Settings.table_exists():
            s = Settings.get_or_none(name="gitlab_url")
            if s is not None:
                gitlab_url = s.value
            s = Settings.get_or_none(name="private_token")
            if s is not None:
                private_token = s.value
    app.logger.debug("gitlab_url: " + gitlab_url)
    app.logger.debug("private_token: " + private_token)
    return render_template('admin.html', name="admin", gitlab_url=gitlab_url,
                           private_token=private_token)


@app.route('/web_hook/', methods=['POST'])
def web_hook():
    ret = dispatch(json.loads(request.get_data()))
    return jsonify(ret)


if __name__ == '__main__':
    # init_mariadb()
    port = os.getenv("PORT")
    app.run(debug=True, host='0.0.0.0', port=port)
