# coding=utf-8

"""
    webhook_handler.py
"""
from builtins import print

import gitlab
import click
import json
from ga.services.webhookservice import dispatch
from ga.services import gitlabservice
from ga.models.gitlab_analytics_models import *


@click.group()
def main():
    pass


@main.command()
@click.option('--log-path', '-i', required=True, help='Path of hook log')
@click.option('--gitlab-url', '-u', required=True, help='Url of Gitlab')
@click.option('--private-token', '-k', required=True, help='Private Key')
def event_info(**options):
    gitlabservice._gl = gitlab.Gitlab(options['gitlab_url'], options['private_token'])

    line_num = 0
    for line in open(options['log_path']):
        line_num += 1

        try:
            data = json.loads(line[0:-1].replace('\n', '\\n'))
            # if data['data']['object_kind'] == 'merge_request':
            #     ret = dispatch(data['data'])
            #     print("line:{}, ret:{}".format(line_num, ret))
            # elif data['data']['object_kind'] == 'note':
            #     ret = dispatch(data['data'])
            #     print("line:{}, ret:{}".format(line_num, ret))
            # elif data['data']['object_kind'] == 'wiki_page':
            #     data['data']['timestamp'] = data['timestamp']
            #     ret = dispatch(data['data'])
            #     print("line:{}, ret:{}".format(line_num, ret))
            #
            #     # 模拟不同时间修改，wiki的创建与修改时间没法通过事件和api读取
            #     time.sleep(1)
            # elif data['data']['object_kind'] == 'issue':
            #     ret = dispatch(data['data'])
            #     print("line:{}, ret:{}".format(line_num, ret))
            # elif data['data']['object_kind'] == 'push':
            if data['data']['object_kind'] == 'push':
                ret = dispatch(data['data'])
                print("line:{}, ret:{}".format(line_num, ret))

        except ValueError as e:
            print(e)
            print("line:{} message:{}".format(line_num, line))


@main.command()
@click.option('--gitlab-url', '-u', required=True, help='Url of Gitlab')
@click.option('--private-token', '-k', required=True, help='Private Key')
@click.option('--project-id', '-p', required=True, help='Project id')
@click.option('--from-time', '-t', required=True, help='Git lab time like: 2018-11-02T00:00:00Z')
def commit_history(**options):
    # database.drop_tables([GitlabCommits])
    database.create_tables([GitlabCommits])

    gitlabservice._gl = gitlab.Gitlab(options['gitlab_url'], options['private_token'])
    project = gitlabservice.get_project(options['project_id'])
    commit_count = 0
    for commit_detail in gitlabservice.get_commit_list(options['project_id'], options['from_time']):
        # merge的和提交超过2000行的忽略
        # 仓库的第一个commit，parent_ids = 0
        # merge 操作, parent_ids = 2
        l = len(commit_detail.parent_ids)
        parent_id = ''
        if l > 1:
            continue
        elif l == 1:
            parent_id = commit_detail.parent_ids[0]

        commit_count = commit_count + 1
        GitlabCommits().insert(project=options['project_id'],
                               project_path=project.name_with_namespace,
                               commit_id=commit_detail.id,
                               title=commit_detail.title,
                               created_at=gitlabservice.get_datetime(commit_detail.created_at),
                               message=commit_detail.message,
                               author_email=commit_detail.author_email,
                               author_name=commit_detail.author_name,
                               authored_date=gitlabservice.get_datetime(commit_detail.authored_date),
                               committed_date=gitlabservice.get_datetime(commit_detail.committed_date),
                               committer_email=commit_detail.committer_email,
                               committer_name=commit_detail.committer_name,
                               ignore=0,
                               line_additions=commit_detail.stats['additions'],
                               line_deletions=commit_detail.stats['deletions'],
                               line_total=commit_detail.stats['total'],
                               parent_id=parent_id,
                               ).on_conflict_replace().execute()

    print("commit count: {}".format(commit_count))


@main.command()
@click.option('--gitlab-url', '-u', required=True, help='Url of Gitlab')
@click.option('--private-token', '-k', required=True, help='Private Key')
@click.option('--project-id', '-p', required=True, help='Project id')
def issue_history(**options):
    gitlabservice._gl = gitlab.Gitlab(options['gitlab_url'], options['private_token'])
    project = gitlabservice.get_project(options['project_id'])

    database.create_tables([GitlabIssues, GitlabIssueComment])

    issue_count = 0
    issue_comment_count = 0

    for issue_data in gitlabservice.get_issue_list(options['project_id']):
        # 兼容assignee忘记指定的情况
        assignee = issue_data.author['username']
        if len(issue_data.assignees) is 1:
            assignee = issue_data.assignees[0]['username']

        issue_count = issue_count + 1
        GitlabIssues().insert(project=options['project_id'],
                              project_path=project.name_with_namespace,
                              author_name=issue_data.author['username'],
                              issue_id=issue_data.id,
                              created_at=gitlabservice.get_datetime(issue_data.created_at),
                              ignore=0,
                              assignee=assignee,
                              title=issue_data.title,
                              ).on_conflict_replace().execute()

        for comment_data in issue_data.notes.list():
            issue_comment_count = issue_comment_count + 1
            GitlabIssueComment.insert(project=options['project_id'],
                                      project_path=project.name_with_namespace,
                                      author_name=comment_data.author['username'],
                                      comment_id=comment_data.id,
                                      issue_id=issue_data.id,
                                      created_at=gitlabservice.get_datetime(comment_data.created_at),
                                      ignore=0,
                                      content_length=len(comment_data.body)
                                      ).on_conflict_replace().execute()

    print("issue count: {}".format(issue_count))
    print("comment count: {}".format(issue_comment_count))


@main.command()
@click.option('--gitlab-url', '-u', required=True, help='Url of Gitlab')
@click.option('--private-token', '-k', required=True, help='Private Key')
@click.option('--project-id', '-p', required=True, help='Project id')
@click.option('--page-start', '-n', required=True, type=int, help='Page No Start')
@click.option('--page-count', '-c', required=True, type=int, help='Page Count')
def mr_history(**options):
    gitlabservice._gl = gitlab.Gitlab(options['gitlab_url'], options['private_token'])
    project = gitlabservice.get_project(options['project_id'])

    # database.drop_tables([GitlabMergeRequest, GitlabMRInitiatorComment, GitlabMRAssigneeComment])
    database.create_tables([GitlabMergeRequest, GitlabMRInitiatorComment, GitlabMRAssigneeComment])

    merge_count = 0
    initiator_comment_count = 0
    assignee_comment_count = 0
    merge_count = 0
    for page_no in range(options['page_start'], options['page_start'] + options['page_count']):
        for merge_request_data in gitlabservice.get_mergerequest_list(options['project_id'], page_no):
            milestone_id = None if merge_request_data.milestone is None else merge_request_data.milestone['id']

            # 不指定assignee的merge_request不统计，不是规范的codereview
            if merge_request_data.assignee is None or not merge_request_data.assignee['id']:
                continue

            merge_count = merge_count + 1
            GitlabMergeRequest.insert(project=options['project_id'],
                                      project_path=project.name_with_namespace,
                                      author_name=merge_request_data.author['username'],
                                      merge_request_id=merge_request_data.id,
                                      created_at=gitlabservice.get_datetime(merge_request_data.created_at),
                                      ignore=0,
                                      title=merge_request_data.title,
                                      milestone_id=milestone_id,
                                      assignee=merge_request_data.assignee['username']
                                      ).on_conflict_replace().execute()

            GitlabMRInitiatorComment.insert(project=options['project_id'],
                                            project_path=project.name_with_namespace,
                                            author_name=merge_request_data.author['username'],
                                            comment_id=0,
                                            merge_request_id=merge_request_data.id,
                                            created_at=gitlabservice.get_datetime(merge_request_data.created_at),
                                            ignore=0,
                                            content_length=len(merge_request_data.description)
                                            ).on_conflict_replace().execute()

        for comment_data in merge_request_data.notes.list():
            if comment_data.author['id'] == merge_request_data.author['id']:
                initiator_comment_count = initiator_comment_count + 1
                # 评论自己的request说明很好地配合codereview
                GitlabMRInitiatorComment.insert(project=options['project_id'],
                                                project_path=project.name_with_namespace,
                                                author_name=comment_data.author['username'],
                                                comment_id=comment_data.id,
                                                merge_request_id=merge_request_data.id,
                                                created_at=gitlabservice.get_datetime(comment_data.created_at),
                                                ignore=0,
                                                content_length=len(comment_data.body)
                                                ).on_conflict_replace().execute()
            else:
                assignee_comment_count = assignee_comment_count + 1
                # 很好地进行对别人的codereview与参与讨论
                GitlabMRAssigneeComment.insert(project=options['project_id'],
                                               project_path=project.name_with_namespace,
                                               author_name=comment_data.author['username'],
                                               comment_id=comment_data.id,
                                               merge_request_id=merge_request_data.id,
                                               created_at=gitlabservice.get_datetime(comment_data.created_at),
                                               ignore=0,
                                               content_length=len(comment_data.body)
                                               ).on_conflict_replace().execute()

    print('merge_count: {}'.format(merge_count))
    print('initiator_comment_count: {}'.format(initiator_comment_count))
    print('assignee_comment_count: {}'.format(assignee_comment_count))


# @main.command()
# @click.option('--gitlab-url', '-u', required=True, help='Url of Gitlab')
# @click.option('--private-token', '-k', required=True, help='Private Key')
# @click.option('--project-id', '-p', required=True, help='Project id')
# def wiki_history(**options):
#     gitlabservice._gl = gitlab.Gitlab(options['gitlab_url'], options['private_token'])
#     project = gitlabservice.get_project(options['project_id'])
#
#     wiki_count = 0
#     for wiki_data in gitlabservice.get_wiki_list(options['project_id']):
#         wiki_count = wiki_count + 1
#         # GitlabWikiCreate().insert(project=options['project_id'],
#         #                           project_path=project.name_with_namespace,
#         #                           author_name=wiki_data['user']['username'],
#         #                           wiki_id=wiki_data['object_attributes']['slug'],
#         #                           created_at=datetime.datetime.fromtimestamp(wiki_data['timestamp']) if 'timestamp' in wiki_data else datetime.datetime.now(),
#         #                           ignore=0,
#         #                           title=wiki_data['object_attributes']['title'],
#         #                           content_length=len(wiki_data['object_attributes']['content'])
#         #                           ).on_conflict_replace().execute()


if __name__ == '__main__':
    main()
