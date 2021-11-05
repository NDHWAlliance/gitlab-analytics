import datetime
import json
import os
from datetime import datetime as dt
import logging
import click
from flask import current_app as app
from flask.cli import with_appcontext
from ..services import dbservice
from ..services import gitlabservice
from ..services.projectservice import ProjectService



@click.command('hook_all')
@with_appcontext
def hook_all(**options):
    """
    把所有项目都加上hook
    :param options:
    :return:
    """
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logger = logging.getLogger("ga")
    # logger.setLevel(logging.INFO)
    # logger.debug("hi")
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    dbservice.load_settings()
    for project in gitlabservice.get_projects():
        print(f"{project['hooked']}\t{project['url']}")
        if not project['hooked']:
            # print(app.config['external_url'])
            print(gitlabservice.add_hook(project['id']))
