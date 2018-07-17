# coding=utf-8

"""
    webhook_handler.py
"""

import click
import gitlab_api
import requests
from utils import get_config


@click.group()
def main():
    pass


@main.command()
def list_ids(**options):
    projects = gitlab_api.list_all_projects()
    for project in projects:
        print("id:{}, web_url:{}".format(project.id, project.web_url))


@main.command()
@click.option('--project-ids', '-i', help='Input project-ids like "1,3,15", or just "all"')
def add_hook(**options):
    ids = []
    if not options['project_ids']:
        projects = gitlab_api.list_all_projects()
        for project in projects:
            ids.append(project.id)
    else:
        ids = options['project_ids'].split(',')

    web_hook = get_config('gitlab', 'hook')
    for project_id in ids:
        hooks = gitlab_api.list_hooks(project_id)

        is_hooked = False
        for hook in hooks:
            if hook.url == web_hook:
                is_hooked = True

        if not is_hooked:
            print("Add hook [{}] to id [{}]".format(web_hook, project_id))
            gitlab_api.add_hook(project_id, web_hook)


if __name__ == '__main__':
    main()
