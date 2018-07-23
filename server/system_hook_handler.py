# coding=utf-8

"""
    webhook_handler.py
"""

from gitlab import GitlabGetError
from ga_config import ga_config

import gitlab_api
import sys


def dispatch(event_data):
    mod = sys.modules[__name__]
    func = getattr(mod, event_data['event_name'], None)

    if func is not None:
        try:
            func(event_data)
        except GitlabGetError as e:
            return {"ret": e.response_code, "message": e.error_message, "data": event_data}

    return {"ret": 0}


def project_create(event_data):
    gitlab_api.add_hook(event_data['project_id'], ga_config['external_url'])
