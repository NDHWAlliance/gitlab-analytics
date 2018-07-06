from flask import Flask, request, jsonify
import os
import json
from gitlab_analytics_models import *
from webhook_handler import dispatch
from flask import render_template

app = Flask(__name__)


@app.route("/", methods=['GET'])
def root():
    # TODO read config values from DB
    gitlab_url = ""
    private_token = ""
    return render_template('admin.html', name="admin", gitlab_url=gitlab_url,
                           private_token=private_token)


def intialization():
    # setup charset
    # create readonly user
    # create tables
    pass


@app.route("/admin", methods=['GET', 'POST'])
def admin(gitlab_url="", private_token=""):
    # TODO
    # if table not exists: do some intialization such as create tables
    # save config values into tables
    # TODO when will webhooks be added to gitlab repos?
    need_intialization = False
    if need_intialization:
        intialization()
    return render_template('admin.html', name="admin", gitlab_url=gitlab_url,
                           private_token=private_token)


@app.route('/web_hook/', methods=['POST'])
def web_hook():
    ret = dispatch(json.loads(request.get_data()))
    return jsonify(ret)


def init_mariadb():
    # all the env here are defined in docker-compose.yml
    mysql_host = os.getenv("MYSQL_HOST")
    mysql_port = os.getenv("MYSQL_PORT")
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    mysql_database = os.getenv("MYSQL_DATABASE")
    print("init_mariadb")
    print(mysql_host)

    database.database = mysql_database
    database.connect_params = {'host': mysql_host, 'port': int(mysql_port),
                               'user': mysql_user,
                               'password': str(mysql_password),
                               'charset': 'utf8', 'use_unicode': True}


if __name__ == '__main__':
    # init_mariadb()
    port = os.getenv("PORT")
    app.run(debug=True, host='0.0.0.0', port=port)
