import logging
import datetime
from datetime import datetime as dt
from flask import current_app as app
import gitlab
from .gitlabservice import gitlab_time_str_to_local_time
from .gitlabservice import _get_gl
from ..models.gitlab_analytics_models import GitlabCommits
from ..models.gitlab_analytics_models import database
from pprint import pprint

"""
TODO 业务需求

* 命令行定时执行
* 导入 commits、issue、wiki、comments 等数据
* 可以重复执行，历史数据不会重复受理

"""


class Commit:

    def __init__(self, project_id, project_path, project_commit):
        c = project_commit
        self.project_id = project_id
        self.project_path = project_path[:128]
        self.commit_id = c.id
        self.title = c.title[:72]
        self.created_at = gitlab_time_str_to_local_time(c.created_at)
        self.parent_ids = len(c.parent_ids)
        self.message = c.message[:255]

        self.author_name = c.author_name[:64]
        self.author_email = c.author_email[:64]
        self.authored_date = gitlab_time_str_to_local_time(c.authored_date)

        self.committer_name = c.committer_name[:64]
        self.committer_email = c.committer_email[:64]
        self.committed_date = gitlab_time_str_to_local_time(c.committed_date)

        self.line_additions = 0
        self.line_deletions = 0
        self.line_total = 0
        self.ignore = 0

    @staticmethod
    def http_get(gl, project_id, commit_id):
        logger = logging.getLogger("ga")
        url = ('/projects/%(project_id)s/repository/commits/%(commit_id)s'
               % {'project_id': project_id, 'commit_id': commit_id})
        try:
            data = gl.http_get(url)
            return data
        except gitlab.GitlabHttpError as exc1:
            logger.error("http status code: {}".format(exc1.response_code))
            logger.error(url)
            return False
        except gitlab.GitlabParsingError as exc2:
            logger.error("error: {}".format(exc2.error_message))
            logger.error(url)
            return False

    def detail(self, gl):
        logger = logging.getLogger("ga")
        if self.parent_ids > 1:
            # merge 操作，直接忽略掉detail吧
            self.ignore = 1
            return False

        data = Commit.http_get(gl, self.project_id, self.commit_id)
        if data is False:
            logger.error("failed to get detail of {}".format(self.url()))
            self.ignore = 1
            return False

        # FIXME http://git.youle.game/denghui02/ChainChronicle/commit/f5da706a6fe205e7eca435c1086c8c9982cdd7e3
        # 2018-06-10 11:39:42 访问上面的link 会 502 错误，怎么办？
        self.line_additions = data['stats']['additions']
        self.line_deletions = data['stats']['deletions']
        self.line_total = data['stats']['total']
        return True

    def url(self):
        return 'http://git.youle.game/' + self.project_path \
               + '/commit/' + self.commit_id

    def __iter__(self):
        yield 'project', self.project_id
        yield 'project_path', self.project_path
        # FIXME commit or commit_id ?
        yield 'commit_id', self.commit_id
        yield 'title', self.title
        yield 'created_at', self.created_at
        yield 'parent_ids', self.parent_ids
        yield 'message', self.message
        yield 'author_name', self.author_name
        yield 'author_email', self.author_email
        yield 'authored_date', self.authored_date
        yield 'committer_name', self.committer_name
        yield 'committer_email', self.committer_email
        yield 'committed_date', self.committed_date
        yield 'line_additions', self.line_additions
        yield 'line_deletions', self.line_deletions
        yield 'line_total', self.line_total
        yield 'ignore', self.ignore


class ProjectService:
    def __init__(self, project, no_skip):
        self.project = project
        self._no_skip = no_skip
        self._commit_data = []

    @staticmethod
    def commit_exists_in_db(project_id, commit_id):
        r = GitlabCommits.get_or_none(
            # FIXME commit or commit_id ?
            GitlabCommits.commit_id == commit_id,
            GitlabCommits.project == project_id)
        return r is not None

    def update_commits(self, since_date):
        logger = logging.getLogger("ga")

        # TODO 这里是不是只能获取最近一年的 events？ 如果想导入仓库所有的历史数据，是不是不能用这个办法？
        events = self.get_project_events(since_date)
        for event in events:
            logger.info(
                "{author}, {project}, {ref_type}/{ref}, commits: {count}, {commit_to}".format(
                    **{
                        "author": event.author_username,
                        "project": self.project.path_with_namespace,
                        "count": event.push_data['commit_count'],
                        "ref_type": event.push_data['ref_type'],
                        "ref": event.push_data['ref'],
                        "commit_to": event.push_data['commit_to']
                    }))
            commits = self.get_commits_in_event(event)
            for commit in commits:
                self.log_commit(commit)

    def import_commits(self):
        for commit in self.project.commits.list(as_list=False, limit=10):
            self.log_commit(commit)

    def get_project_events(self, since_date):
        logger = logging.getLogger("ga")
        # https://docs.gitlab.com/ee/api/events.html#date-formatting
        # accroding to the above document, since_date should be "YYYY-MM-DD"
        # format
        delta = datetime.timedelta(hours=24)
        since_date2 = since_date - delta
        sincestr = since_date2.strftime("%Y-%m-%d")
        logger.debug(
            "find project events after {}({})".format(sincestr, since_date))
        events = self.project.events.list(as_list=False, after=sincestr)
        for event in events:
            # FIXME 这里一共有几种 action_name ？目前看到的有下面这些
            # pushed to
            # pushed new
            # deleted
            # joined
            # commented on
            # opened
            # 2018-06-13 17:36:33 owen 忽略掉tag commit
            if event.action_name[:6] == 'pushed' and \
                    event.push_data['ref_type'] == 'branch':
                # created_at = Anaylitics.utc_timestr_parse(event.created_at)
                created_at = gitlab_time_str_to_local_time(event.created_at)
                if created_at >= since_date:
                    logger.debug("event created time, gitlab: {}, local: {}".format(event.created_at, created_at))
                    yield event

    def get_commits_in_event(self, event):
        project = self.project
        logger = logging.getLogger("ga")
        commit_count = event.push_data['commit_count']
        commit_to_id = event.push_data['commit_to']
        if commit_count == 1:
            # you will get 403 error when the project does not have repo
            try:
                yield project.commits.get(commit_to_id, stats=False)
            except gitlab.exceptions.GitlabGetError as ex:
                logger.error(ex.error_message)
            return

        arguments = {"as_list": False, "ref_name": event.push_data['ref']}

        # 如果 commit_from is None，那么是一个新分支
        if event.push_data['commit_from'] is not None:
            commit_id = event.push_data['commit_from']
            commit_from = project.commits.get(commit_id, stats=False)
            sincestr = commit_from.committed_date
            arguments['since'] = sincestr

        try:
            commits = project.commits.list(**arguments)
        except gitlab.exceptions.GitlabListError as ex:
            logger.error(ex.error_message)
            return

        # 返回的 commits 是按时间逆序排列。
        # 先找到 commit_to，然后向前找到 commit_count 个 commit（含 commit_to）
        while True:
            commit = next(commits)
            if commit.id == commit_to_id:
                break
        yield commit
        count = 1
        while count < commit_count:
            commit = next(commits)
            yield commit
            count += 1

    def updatedb(self):
        logger = logging.getLogger("ga")
        data_source = self._commit_data
        if len(data_source) == 0:
            return
        logger.info("updating database with {} commits...".format(len(data_source)))
        with database.atomic():
            for idx in range(0, len(data_source), 1000):
                # TODO replace_many 会导致条目的id发生变化！！！是否有问题？
                GitlabCommits.replace_many(data_source[idx:idx + 1000]).execute()
        self._commit_data = []

    def log_commit(self, commit):
        logger = logging.getLogger("ga")
        project = self.project
        if not self._no_skip and ProjectService.commit_exists_in_db(project.id, commit.id):
            logger.info("skip {} {} {}".format(commit.authored_date, commit.author_name, commit.id))
            return
        c = Commit(project.id, project.path_with_namespace, commit)
        logger.info(
            "{}, {}, {}".format(c.authored_date, c.author_name, c.title))
        logger.info(c.url())
        c.detail(_get_gl())
        self._commit_data.append(dict(c))
        self.updatedb()
