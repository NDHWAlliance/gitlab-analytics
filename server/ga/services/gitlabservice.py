import datetime
import gitlab

from flask import current_app as app

_gl = None


def _get_gl():
    if _gl is not None:
        return _gl
    url = app.config['gitlab_url']
    private_token = app.config['private_token']
    return gitlab.Gitlab(url, private_token=private_token)


def is_hooked(project):
    web_hook = app.config['external_url']
    for hook in project.hooks.list():
        if hook.url == web_hook:
            return True
    return False


def get_project(project_id):
    return _get_gl().projects.get(project_id)


def get_projects():
    gitlab_projects = _get_gl().projects.list(order_by='last_activity_at',
                                              as_list=False, limit=10)
    projects = []
    for project in gitlab_projects:
        if is_hooked(project):
            hooked = 1
        else:
            hooked = 0

        projects.append({
            "id": project.id,
            "url": project.web_url,
            "hooked": hooked,
            "loading": 0

        })
    return projects


def add_hook(project_id):
    project = _get_gl().projects.get(project_id)
    project.hooks.create({'url': app.config['external_url'],
                          'push_events': True, 'issues_events': True,
                          'merge_requests_events': True,
                          'tag_push_events': True, 'note_events': True,
                          'job_events': True, 'pipeline_events': True,
                          'wiki_page_events': True})


def remove_hook(project_id):
    url = app.config['external_url']
    project = _get_gl().projects.get(project_id)
    hooks = project.hooks.list()
    hook_id = None
    for hook in hooks:
        if hook.url == url:
            hook_id = hook.id
            break
    if hook_id is not None:
        project.hooks.delete(hook_id)


def get_datetime(origin_str):
    return datetime.datetime.strptime(origin_str[0:19],
                                      "%Y-%m-%d{}%H:%M:%S".format(
                                          origin_str[10:11]))


def get_commit_detail(project_id, commit_id):
    return _get_gl().projects.get(project_id).commits.get(commit_id)


def get_commit_list(project_id, str_time):
    dt = get_datetime(str_time)
    dt_7day = dt + datetime.timedelta(days=7) - datetime.timedelta(seconds=1)
    dt_7day = dt_7day if dt_7day < datetime.datetime.now() else datetime.datetime.now()

    now = datetime.datetime.now()
    while dt_7day < now:
        commits = _get_gl().projects.get(project_id).commits.list(since=dt.strftime('%Y-%m-%dT%H:%M:%SZ'), until=dt_7day.strftime('%Y-%m-%dT%H:%M:%SZ'))
        dt = dt_7day + datetime.timedelta(seconds=1)
        dt_7day = dt_7day + datetime.timedelta(days=7)
        dt_7day = dt_7day if dt_7day < now else now
        for commit in commits:
            yield get_commit_detail(project_id, commit.id)


def get_issue_list(project_id):
    return _get_gl().projects.get(project_id).issues.list()


def get_mergerequest_list(project_id, page_no):
    return _get_gl().projects.get(project_id).mergerequests.list(page=page_no, order_by='created_at', sort='asc')


def get_wiki_list(project_id):
    project = _get_gl().projects.get(project_id)
    for wiki_data in project.wikis.list():
        yield project.wikis.get(wiki_data.slug)

