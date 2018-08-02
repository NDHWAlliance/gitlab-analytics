# coding=utf-8

"""
    webhook_handler.py
"""
import sys

from gitlab import GitlabGetError

from . import gitlabservice


def dispatch(event_data):
    mod = sys.modules[__name__]
    func = getattr(mod, event_data['event_name'], None)

    if func is not None:
        try:
            func(event_data)
        except GitlabGetError as e:
            return {"ret": e.response_code, "message": e.error_message,
                    "data": event_data}

    return {"ret": 0}


def project_create(event_data):
    gitlabservice.add_hook(event_data['project_id'])
