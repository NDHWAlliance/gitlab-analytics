# coding=utf-8

"""
    webhook_handler.py
"""
import sys

from peewee import *

database = MySQLDatabase('gitlab_analytics', **{'charset': 'utf8', 'use_unicode': True, 'host': '127.0.0.1', 'user': 'ga', 'password': '4t9wegcvbYSd'})
database.execute_sql('alter database gitlab_analytics default character set utf8 collate utf8_general_ci')


class BaseModel(Model):
    class Meta:
        database = database


class GitlabCommits(BaseModel):
    author_email = CharField(index=True)
    author_name = CharField(index=True)
    authored_date = DateTimeField(index=True)
    commit_id = CharField(column_name='commit_id')
    committed_date = DateTimeField()
    committer_email = CharField()
    committer_name = CharField()
    created_at = DateTimeField()
    ignore = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    line_additions = IntegerField(null=True)
    line_deletions = IntegerField(null=True)
    line_total = IntegerField(null=True)
    message = CharField()
    parent_ids = IntegerField()
    project = IntegerField(column_name='project_id')
    project_path = CharField()
    title = CharField()

    class Meta:
        table_name = 'gitlab_commits'
        indexes = (
            (('commit_id', 'project'), True),
        )


class GitlabIssues(BaseModel):
    author_name = CharField(index=True)
    issue_id = CharField(column_name='issue_id')
    created_at = DateTimeField(index=True)
    ignore = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    assignee = CharField(index=True)
    title = CharField()
    project = IntegerField(column_name='project_id')
    project_path = CharField()
    title = CharField()

    class Meta:
        table_name = 'gitlab_issues'
        indexes = (
            (('issue_id', 'project'), True),
        )


class GitlabWikiCreate(BaseModel):
    author_name = CharField(index=True)
    wiki_id = CharField(column_name='wiki_id')
    created_at = DateTimeField(index=True)
    ignore = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    content_length = IntegerField()
    title = CharField()
    project = IntegerField(column_name='project_id')
    project_path = CharField()

    class Meta:
        table_name = 'gitlab_wiki_create'
        indexes = (
            (('wiki_id', 'project'), True),
        )


class GitlabWikiUpdate(BaseModel):
    author_name = CharField(index=True)
    wiki_id = CharField(column_name='wiki_id')
    created_at = DateTimeField(index=True)
    ignore = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    content_length = IntegerField()
    title = CharField()
    project = IntegerField(column_name='project_id')
    project_path = CharField()

    class Meta:
        table_name = 'gitlab_wiki_update'
        indexes = (
            (('wiki_id', 'project', 'created_at'), True),
        )


class GitlabWikiComments(BaseModel):
    author_name = CharField(index=True)
    comment_id = CharField()
    created_at = DateTimeField(index=True)
    ignore = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    content_length = IntegerField()
    title = CharField()
    project = IntegerField(column_name='project_id')
    project_path = CharField()

    class Meta:
        table_name = 'gitlab_wiki_update'
        indexes = (
            (('comment_id', 'project'), True),
        )


if __name__ == '__main__':
    database.create_tables([GitlabWikiCreate, GitlabWikiUpdate])
