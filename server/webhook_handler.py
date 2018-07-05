# coding=utf-8

"""
    webhook_handler.py
"""
import datetime

import peewee
import pymysql
from gitlab import GitlabGetError

import gitlab_api
from gitlab_analytics_models import *
import sys


def dispatch(event_data):
    mod = sys.modules[__name__]
    func = getattr(mod, event_data['object_kind'], None)

    if func is not None:
        try:
            func(event_data)
        except GitlabGetError as e:
            return {"ret": e.response_code, "message": e.error_message, "data": event_data}

    return {"ret": 0}


def push(push_data):
    for commit in push_data['commits']:
        commit_detail = gitlab_api.get_commit_detail(push_data['project_id'], commit['id'])

        # merge的和提交超过2000行的忽略
        if len(commit_detail.parent_ids) is not 1:
            continue

        GitlabCommits().insert(project=push_data['project']['id'],
                               project_path=push_data['project']['path_with_namespace'],
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


def issue(issue_data):
    # 更新的issue不做统计
    if not issue_data['object_attributes']['created_at'] != issue_data['object_attributes']['updated_at']:
        return

    # 兼容assignee忘记指定的情况
    assignee = issue_data['user']['username']
    if 'assignees' in issue_data.keys() and len(issue_data['assignees']) is 1:
        assignee = issue_data['assignees'][0]['username']

    GitlabIssues().insert(project=issue_data['project']['id'],
                          project_path=issue_data['project']['path_with_namespace'],
                          author_name=issue_data['user']['username'],
                          issue_id=issue_data['object_attributes']['id'],
                          created_at=gitlab_api.get_datetime(issue_data['object_attributes']['created_at']),
                          ignore=0,
                          assignee=assignee,
                          title=issue_data['object_attributes']['title'],
                          ).on_conflict_replace().execute()


def wiki_page(wiki_data):
    # delete 的action不处理
    if wiki_data['object_attributes']['action'] == 'delete':
        return

    # 首次创建统计所有的字数
    if wiki_data['object_attributes']['action'] == 'create':
        GitlabWikiCreate().insert(project=wiki_data['project']['id'],
                                  project_path=wiki_data['project']['path_with_namespace'],
                                  author_name=wiki_data['user']['username'],
                                  wiki_id=wiki_data['object_attributes']['slug'],
                                  created_at=datetime.datetime.now(),
                                  ignore=0,
                                  title=wiki_data['object_attributes']['title'],
                                  content_length=len(wiki_data['object_attributes']['content'])
                                  ).on_conflict_replace().execute()
        GitlabWikiUpdate().insert(project=wiki_data['project']['id'],
                                  project_path=wiki_data['project']['path_with_namespace'],
                                  author_name=wiki_data['user']['username'],
                                  wiki_id=wiki_data['object_attributes']['slug'],
                                  created_at=datetime.datetime.now(),
                                  ignore=0,
                                  title=wiki_data['object_attributes']['title'],
                                  content_length=len(wiki_data['object_attributes']['content'])
                                  ).on_conflict_replace().execute()
        print('{} {}'.format(wiki_data['object_attributes']['url'], len(wiki_data['object_attributes']['content'])))

    # 更新的时候比对字数
    if wiki_data['object_attributes']['action'] == 'update':
        create_wiki = GitlabWikiCreate.get_or_none(project=wiki_data['project']['id'], wiki_id=wiki_data['object_attributes']['slug'])
        if create_wiki:
            content_additions = len(wiki_data['object_attributes']['content']) - create_wiki.content_length
            if content_additions > 0:
                print('{} {} {} {}'.format(wiki_data['object_attributes']['url'], content_additions, len(wiki_data['object_attributes']['content']), create_wiki.content_length))
                GitlabWikiUpdate().insert(project=wiki_data['project']['id'],
                                          project_path=wiki_data['project']['path_with_namespace'],
                                          author_name=wiki_data['user']['username'],
                                          wiki_id=wiki_data['object_attributes']['slug'],
                                          created_at=datetime.datetime.now(),
                                          ignore=0,
                                          title=wiki_data['object_attributes']['title'],
                                          content_length=content_additions,
                                          ).on_conflict_replace().execute()
                GitlabWikiCreate.update(content_length=len(wiki_data['object_attributes']['content'])).where(
                    GitlabWikiCreate.project == wiki_data['project']['id'], GitlabWikiCreate.wiki_id == wiki_data['object_attributes']['slug']).execute()
