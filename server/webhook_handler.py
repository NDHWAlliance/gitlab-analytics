# coding=utf-8

"""
    webhook_handler.py
"""
import datetime

from gitlab import GitlabGetError

import gitlab_api
from gitlab_analytics_models import *
import sys


def add_hook(**options):
    ids = []
    if not options['project_ids']:
        projects = gitlab_api.list_all_projects()
        for project in projects:
            ids.append(project.id)
    else:
        ids = options['project_ids'].split(',')

    web_hook = options['web_hook']
    for project_id in ids:
        hooks = gitlab_api.list_hooks(project_id)

        is_hooked = False
        for hook in hooks:
            if hook.url == web_hook:
                is_hooked = True

        if not is_hooked:
            gitlab_api.add_hook(project_id, web_hook)


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
                               parent_id=commit_detail.parent_ids[0],
                               ).on_conflict_replace().execute()


def issue(issue_data):
    # 更新的issue不做统计
    if issue_data['object_attributes']['created_at'] != issue_data['object_attributes']['updated_at']:
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
                                  created_at=datetime.datetime.fromtimestamp(wiki_data['timestamp']) if 'timestamp' in wiki_data else datetime.datetime.now(),
                                  ignore=0,
                                  title=wiki_data['object_attributes']['title'],
                                  content_length=len(wiki_data['object_attributes']['content'])
                                  ).on_conflict_replace().execute()
        GitlabWikiUpdate().insert(project=wiki_data['project']['id'],
                                  project_path=wiki_data['project']['path_with_namespace'],
                                  author_name=wiki_data['user']['username'],
                                  wiki_id=wiki_data['object_attributes']['slug'],
                                  created_at=datetime.datetime.fromtimestamp(wiki_data['timestamp']) if 'timestamp' in wiki_data else datetime.datetime.now(),
                                  ignore=0,
                                  title=wiki_data['object_attributes']['title'],
                                  content_length=len(wiki_data['object_attributes']['content'])
                                  ).on_conflict_replace().execute()
        # print('{} {}'.format(wiki_data['object_attributes']['url'], len(wiki_data['object_attributes']['content'])))

    # 更新的时候比对字数
    if wiki_data['object_attributes']['action'] == 'update':
        create_wiki = GitlabWikiCreate.get_or_none(project=wiki_data['project']['id'], wiki_id=wiki_data['object_attributes']['slug'])
        if create_wiki:
            content_additions = len(wiki_data['object_attributes']['content']) - create_wiki.content_length
            if content_additions > 0:
                # print('{} {} {} {}'.format(wiki_data['object_attributes']['url'], content_additions, len(wiki_data['object_attributes']['content']), create_wiki.content_length))
                GitlabWikiUpdate().insert(project=wiki_data['project']['id'],
                                          project_path=wiki_data['project']['path_with_namespace'],
                                          author_name=wiki_data['user']['username'],
                                          wiki_id=wiki_data['object_attributes']['slug'],
                                          created_at=datetime.datetime.fromtimestamp(wiki_data['timestamp']) if 'timestamp' in wiki_data else datetime.datetime.now(),
                                          ignore=0,
                                          title=wiki_data['object_attributes']['title'],
                                          content_length=content_additions,
                                          ).on_conflict_replace().execute()
                GitlabWikiCreate.update(content_length=len(wiki_data['object_attributes']['content'])).where(
                    GitlabWikiCreate.project == wiki_data['project']['id'], GitlabWikiCreate.wiki_id == wiki_data['object_attributes']['slug']).execute()


def merge_request(merge_request_data):
    # open的时候才统计
    if merge_request_data['object_attributes']['action'] != 'open':
        return

    # 不指定assignee的merge_request不统计，不是规范的codereview
    if not merge_request_data['object_attributes']['assignee_id']:
        return

    # print('{} {}'.format(merge_request_data['user']['username'], merge_request_data['assignee']['username']))

    GitlabMergeRequest.insert(project=merge_request_data['project']['id'],
                              project_path=merge_request_data['project']['path_with_namespace'],
                              author_name=merge_request_data['user']['username'],
                              merge_request_id=merge_request_data['object_attributes']['id'],
                              created_at=gitlab_api.get_datetime(merge_request_data['object_attributes']['created_at']),
                              ignore=0,
                              title=merge_request_data['object_attributes']['title'],
                              milestone_id=merge_request_data['object_attributes']['milestone_id'],
                              assignee=merge_request_data['assignee']['username']
                              ).on_conflict_replace().execute()
    GitlabMRInitiatorComment.insert(project=merge_request_data['project']['id'],
                                    project_path=merge_request_data['project']['path_with_namespace'],
                                    author_name=merge_request_data['user']['username'],
                                    comment_id=0,
                                    merge_request_id=merge_request_data['object_attributes']['id'],
                                    created_at=gitlab_api.get_datetime(merge_request_data['object_attributes']['created_at']),
                                    ignore=0,
                                    content_length=len(merge_request_data['object_attributes']['description'])
                                    ).on_conflict_replace().execute()


def note(comment_data):
    if comment_data['object_attributes']['noteable_type'] == 'MergeRequest':
        if comment_data['object_attributes']['author_id'] == comment_data['merge_request']['author_id']:
            # 评论自己的request说明很好地配合codereview
            GitlabMRInitiatorComment.insert(project=comment_data['project']['id'],
                                            project_path=comment_data['project']['path_with_namespace'],
                                            author_name=comment_data['user']['username'],
                                            comment_id=comment_data['object_attributes']['id'],
                                            merge_request_id=comment_data['merge_request']['id'],
                                            created_at=gitlab_api.get_datetime(comment_data['object_attributes']['created_at']),
                                            ignore=0,
                                            content_length=len(comment_data['object_attributes']['note'])
                                            ).on_conflict_replace().execute()
        else:
            # 很好地进行对别人的codereview与参与讨论
            GitlabMRAssigneeComment.insert(project=comment_data['project']['id'],
                                           project_path=comment_data['project']['path_with_namespace'],
                                           author_name=comment_data['user']['username'],
                                           comment_id=comment_data['object_attributes']['id'],
                                           merge_request_id=comment_data['merge_request']['id'],
                                           created_at=gitlab_api.get_datetime(comment_data['object_attributes']['created_at']),
                                           ignore=0,
                                           content_length=len(comment_data['object_attributes']['note'])
                                           ).on_conflict_replace().execute()

    elif comment_data['object_attributes']['noteable_type'] == 'Issue':
        GitlabIssueComment.insert(project=comment_data['project']['id'],
                                  project_path=comment_data['project']['path_with_namespace'],
                                  author_name=comment_data['user']['username'],
                                  comment_id=comment_data['object_attributes']['id'],
                                  issue_id=comment_data['issue']['id'],
                                  created_at=gitlab_api.get_datetime(comment_data['object_attributes']['created_at']),
                                  ignore=0,
                                  content_length=len(comment_data['object_attributes']['note'])
                                  ).on_conflict_replace().execute()
