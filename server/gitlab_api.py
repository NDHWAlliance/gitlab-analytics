# coding=utf-8

"""
    gitlab_api.py
"""

from utils import get_config
import gitlab
import datetime

URL = get_config('gitlab', 'url')
PRIVATE_TOKEN = get_config('gitlab', 'private_token')

GL = gitlab.Gitlab(URL, private_token=PRIVATE_TOKEN)


def get_datetime(origin_str):
    return datetime.datetime.strptime(origin_str[0:19], "%Y-%m-%d{}%H:%M:%S".format(origin_str[10:11]))


def get_commit_detail(project_id, commit_id):
    return GL.projects.get(project_id).commits.get(commit_id)


