import datetime
from datetime import datetime as dt
import logging
import click

from flask.cli import with_appcontext
from ..services import dbservice
from ..services import gitlabservice
from ..services.projectservice import ProjectService

'''
update vs import

update 是增量更新，把仓库最近一段时间内的变化更新到DB中

import 是完全重新导入，把仓库所有到历史记录导入到DB中
'''


@click.command('update')
@click.option('--since', default=None, help='since datetime')
@click.option('--until', default=None, help='until datetime')
@click.option('--project', default=None, help='project')
@click.option('--no-skip', is_flag=True, default=False)
@with_appcontext
def update_history(**options):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("ga")
    logger.setLevel(logging.DEBUG)

    # this command can be invoked from cli: "flask import"
    # 需求是什么？ 把某个仓库的commit记录提交到 db 里
    if options['since'] is None:
        # since = dt.combine(dt.today(), datetime.time.min)
        now = dt.now()
        delta = datetime.timedelta(hours=4)
        since = now - delta
    else:
        since = dt.strptime(options['since'], "%Y-%m-%d %H:%M:%S")

    if options['until'] is None:
        # delta = datetime.timedelta(days=1)
        # until = since + delta
        until = None
    else:
        until = dt.strptime(options['until'], "%Y-%m-%d %H:%M:%S")

    dbservice.load_settings()

    since_date = since
    project_name = options['project']
    if project_name is None:
        logger.info("find project events after {}".format(since_date))
        projects = gitlabservice.get_active_projects(since_date)
    else:
        projects = [gitlabservice.get_project_by_name(project_name)]
    for p in projects:
        ps = ProjectService(p, options['no_skip'])
        ps.update_commits(since_date)


@click.command('import')
@click.option('--project', default=None, help='project')
@click.option('--no-skip', is_flag=True, default=False)
@with_appcontext
def import_history(**options):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("ga")
    logger.setLevel(logging.DEBUG)

    dbservice.load_settings()

    project_name = options['project']
    if project_name is None:
        # TODO 如何避免重复执行？
        projects = gitlabservice.get_active_projects()
    else:
        projects = [gitlabservice.get_project_by_name(project_name)]
    for p in projects:
        ps = ProjectService(p, options['no_skip'])
        ps.import_commits()
