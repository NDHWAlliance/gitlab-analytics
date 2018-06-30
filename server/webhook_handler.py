# coding=utf-8

"""
    webhook_handler.py
"""

import gitlab_api
import gitlab_analytics_models
import json


def push(push_data):
    for commit in push_data['commits']:
        commit_detail = gitlab_api.get_commit_detail(push_data['project_id'], commit['id'])
        gitlab_analytics_models.GitlabCommits().insert(project=2,
                                                       project_path="owen/test",
                                                       commit_id=commit['id'],
                                                       title=commit_detail.title,
                                                       created_at=gitlab_api.get_datetime(commit_detail.created_at),
                                                       message=commit_detail.message,
                                                       author_email=commit_detail.author_email,
                                                       author_name=commit_detail.author_name,
                                                       authored_date=gitlab_api.get_datetime(commit_detail.authored_date),
                                                       committed_date=gitlab_api.get_datetime(commit_detail.committed_date),
                                                       committer_email=commit_detail.committer_email,
                                                       committer_name=commit_detail.committer_name,
                                                       ignore=0,
                                                       line_additions=commit_detail.stats['additions'],
                                                       line_deletions=commit_detail.stats['deletions'],
                                                       line_total=commit_detail.stats['total'],
                                                       ).on_conflict_replace().execute()



