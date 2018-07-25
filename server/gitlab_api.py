# coding=utf-8

"""
    gitlab_api.py
"""

import gitlab
import datetime
from ga_config import ga_config


def get_gl():
    url = ga_config['gitlab_url']
    private_token = ga_config['private_token']
    return gitlab.Gitlab(url, private_token=private_token)


def get_datetime(origin_str):
    return datetime.datetime.strptime(origin_str[0:19], "%Y-%m-%d{}%H:%M:%S".format(origin_str[10:11]))


def get_commit_detail(project_id, commit_id):
    return get_gl().projects.get(project_id).commits.get(commit_id)


def list_all_projects():
    return get_gl().projects.list(order_by='last_activity_at', as_list=False)


def list_hooks(project_id):
    return get_gl().projects.get(project_id).hooks.list()


def add_hook(project_id, url):
    return get_gl().projects.get(project_id).hooks.create({'url': url, 'push_events': True, 'issues_events': True,
                                                           'merge_requests_events': True, 'tag_push_events': True, 'note_events': True,
                                                           'job_events': True, 'pipeline_events': True, 'wiki_page_events': True})

def remove_hook(project_id, url):
    project = get_gl().projects.get(project_id)
    hooks = project.hooks.list()
    hook_id = None
    for hook in hooks:
        if hook.url == url:
            hook_id = hook.id
            break
    if hook_id is not None:
        project.hooks.delete(hook_id)