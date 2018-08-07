import os
from flask import Flask
from flask import request
import flask
import click

app = Flask(__name__)


@app.route("/api/v4/projects")
def api_projects():
    f = os.path.join(app.root_path, "fake_gitlab_response/projects.json")
    body = open(f).read()
    return flask.make_response((body, {"Content-Type": "application/json"}))


@app.route("/api/v4/projects/<project_id>/hooks", methods=["GET", "POST"])
def api_projects_hooks(project_id):
    if request.method == 'POST':
        f = os.path.join(app.root_path,
                         "fake_gitlab_response/add_hook_response.json")
        body = open(f).read()
        return flask.make_response((body, {"Content-Type": "application/json"}))
    body = "[]"
    return flask.make_response((body, {"Content-Type": "application/json"}))


@app.route("/api/v4/projects/<project_id>")
def api_project(project_id):
    f = os.path.join(app.root_path, "fake_gitlab_response/project.json")
    body = open(f).read()
    return flask.make_response((body, {"Content-Type": "application/json"}))


@click.command()
@click.option('--host', default="0.0.0.0")
@click.option('--port', default="8081")
def run(host, port):
    app.run(host=host, port=port)


if __name__ == '__main__':
    run()
