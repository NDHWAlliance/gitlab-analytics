#coding=utf-8

'''
gitlab api
'''

import json
import urllib
import urllib2
import click


class GitApi(object):

    def __init__(self, url, token):
        '''
        初始化
        :param url:
        :param token:
        '''
        self.private_token = token
        self.api_url = url

    def char_convert(self, s):
        '''
        字符转换
        :param s:
        :return:
        '''
        if '/' in str(s):
            return s.replace('/','%2F')
        else:
            return s

    def gitlab_request(self, url, data={}, method=''):
        '''
        请求gitlab的api，并返回响应内容
        :param url:
        :param data:
        :param method:
        :return:
        '''
        result = {}
        result['status'] = True
        headers = {
            'PRIVATE-TOKEN': self.private_token,
        }
        if data:
            data = urllib.urlencode(data)
        else:
            data = None
        req = urllib2.Request(self.api_url + url, headers=headers, data=data)
        if method:
            req.get_method = lambda: method
        try:
            res = urllib2.urlopen(req)
            content = res.read()
            if content:
                result['info'] = json.loads(content)
            else:
                result['info'] = None
        except urllib2.HTTPError,e:
            result['status'] = False
            result['message'] = 'api调用失败：' + str(e)
        return result

    def get_gitlab_group_list(self, order_by='name', sort='asc'):
        '''
        返回组列表
        :param order_by:
        :param sort:
        :return:
        '''
        group_list = []
        url = '/groups?order_by=%s&sort=%s&per_page=10000' % (order_by, sort)
        result = self.gitlab_request(url)
        if result['status']:
            for group in result['info']:
                group_list.append({'id': group['id'], 'name': group['name']})
            result['info'] = group_list
        return result

    def get_gitlab_group_info(self, gid):
        '''
        获取组信息，接受组名或组id
        :param gid:
        :return:
        '''
        if isinstance(gid, (int, str)):
            url = '/groups/' + str(gid)
            result = self.gitlab_request(url)
            return result
        else:
            return {'status':False,'message':'参数有误'}

    def get_gitlab_user_list(self, **kwargs):
        '''
        获取用户列表
        :param kwargs:
        :return:
        '''
        kwargs['per_page'] = 10000
        user_list = []
        url = '/users?' + urllib.urlencode(kwargs)
        result = self.gitlab_request(url)
        if result['status']:
            for user in result['info']:
                user_list.append({'id': user['id'], 'name': user['username']})
            result['info'] = user_list
        return result

    def get_gitlab_userinfo(self, username):
        '''
        获取用户信息
        :param username:
        :return:
        '''
        url = '/users?username=' + username
        result = self.gitlab_request(url)
        return result

    def del_gitlab_user(self, username):
        '''
        删除用户
        :param username:
        :return:
        '''
        result = {}
        result['status'] = True
        userinfo = self.get_gitlab_userinfo(username)
        if userinfo['status']:
            if userinfo['info']:
                url = '/users/%d' % userinfo['info'][0]['id']
                delinfo = self.gitlab_request(url,method='DELETE')
                if not delinfo['status']:
                    result['status'] = False
                    result['message'] = delinfo['message']
            else:
                result['status'] = False
                result['message'] = '用户不存在'
        return result

    def add_gitlab_user(self, data):
        '''
        添加用户
        :param data:
        :return:
        '''
        url = '/users'
        data.setdefault('reset_password', 'true')
        result = self.gitlab_request(url, data=data)
        return result

    def get_gitlab_projects(self, uid):
        '''
        获取用户的项目列表,接受用户名或uid
        :param uid:
        :return:
        '''
        result = {}
        result['status'] = True
        all_projects_info = self.get_gitlab_project_list()
        if all_projects_info:
            all_projects_id = []
            for project in all_projects_info:
                all_projects_id.append({'id': project['id'], 'name': project['name']})
        else:
            return all_projects_info
        owened_project = []
        for pro in all_projects_id:
            project_member = self.gitlab_request('/projects/%d/members/%d' % (pro['id'],uid))
            if project_member['status'] and project_member['info']:
                owened_project.append({'id': pro['id'], 'name': pro['name'], 'access_level': project_member['info']['access_level']})
            else:
                continue
        result['owened_project'] = owened_project
        return result

    def get_gitlab_groups(self, uid):
        '''
        获取用户的组列表
        :param uid:
        :return:
        '''
        result = {}
        result['status'] = True
        all_groups_info = self.get_gitlab_group_list()
        if all_groups_info['status']:
            all_groups_id = []
            for group in all_groups_info['info']:
                all_groups_id.append({'id': group['id'], 'name': group['name']})
        else:
            return all_groups_info
        owend_group = []
        for gro in all_groups_id:
            group_member = self.gitlab_request('/groups/%d/members/%d' % (gro['id'],uid))
            if group_member['status'] and group_member['info']:
                owend_group.append({'id': gro['id'], 'name': gro['name'], 'access_level': group_member['info']['access_level']})
            else:
                continue
        result['owend_group'] = owend_group
        return result

    def get_gitlab_project_list(self):
        '''
        获取项目列表
        :return:
        '''
        project_list = []
        url = '/projects?simple=true&order_by=name&sort=asc&per_page=10000'
        result = self.gitlab_request(url)
        if result['status']:
            for project in result['info']:
                # if project['path_with_namespace'].split('/')[0] == 'evtchina': project_list.append({'id':project['id'],'name':project['name']})
                project_list.append({'id': project['id'], 'name': project['path_with_namespace']})
        else:
            return result
        return project_list

    def get_gitlab_project_info(self, project):
        '''
        获取项目信息,接受完整项目空间或项目id
        :param project:
        :return:
        '''
        url = '/projects/%s' % self.char_convert(project)
        result = self.gitlab_request(url)
        return result

    def get_gitlab_project_member_info(self, project_id, uid):
        '''
        获取项目某成员信息
        :param project_id:
        :param uid:
        :return:
        '''
        url = '/projects/%d/members/%d' % (project_id, uid)
        result = self.gitlab_request(url)
        return result

    def add_gitlab_project_member(self, project_id, uid, access_level):
        '''
        添加项目成员
        :param project_id:
        :param uid:
        :param access_level:
        :return:
        '''
        url = '/projects/%d/members' % project_id
        data = {
            'user_id': uid,
            'access_level': access_level
        }
        result = self.gitlab_request(url, data=data)
        return result

    def test_gitlab_user_access(self, username, project, access_level):
        '''
        检测用户权限
        :param username:
        :param project:
        :param access_level:
        :return:
        '''
        result = {}
        result['status'] = True
        userinfo = self.get_gitlab_userinfo(username)
        if userinfo['info']:
            uid = userinfo['info'][0]['id']
            project_id = self.get_gitlab_project_info(project)['info'].get('id',None)
            if not project_id:
                result['status'] = False
                result['message'] = '项目不存在'
                return result
            member_info = self.get_gitlab_project_member_info(project_id, uid)
            if member_info['status'] and member_info['info']:
                member_access_level = member_info['info']['access_level']
                if access_level > member_access_level:
                    result['status'] = True
                else:
                    result['status'] = False
                    result['message'] = '已拥有该项目权限'
            else:
                result['status'] = True
        else:
            result['status'] = True
        return result

    def updata_gitlab_member_access(self, username, project, access_level):
        '''
        更新用户权限
        :param username:
        :param project:
        :param access_level:
        :return:
        '''
        result = {}
        result['status'] = True
        userinfo = self.get_gitlab_userinfo(username)
        if userinfo['status']:
            if not userinfo['info']:
                data = {
                    'name':username,
                    'username':username,
                    'email':'%s@eventown.com' % username
                }
                addinfo = self.add_gitlab_user(data)
                if not addinfo['status']:
                    result['status'] = False
                    result['message'] = '添加用户失败'
                    return result
                else:
                    uid = addinfo['info']['id']
            else:
                uid = userinfo['info'][0]['id']
            project_id = self.get_gitlab_project_info(project)['info']['id']
            memberinfo = self.get_gitlab_project_member_info(project_id,uid)
            if memberinfo['status']:
                url = '/projects/%d/members/%d?access_level=%d' % (project_id, uid, access_level)
                updateinfo = self.gitlab_request(url,method='PUT')
                if not updateinfo['status']:
                    result['status'] = False
                    result['message'] = '更新权限失败'
            else:
                addmemberinfo = self.add_gitlab_project_member(project_id, uid, access_level)
                if not addmemberinfo['status']:
                    result['status'] = False
                    result['message'] = '添加权限失败'
        else:
            result['status'] = False
            result['message'] = userinfo['message']
        return result

    def get_gitlab_webhook_list(self, project_id):
        '''
        获取hook列表,接受完整项目空间或项目id
        :param project_id:
        :return:
        '''
        url = '/projects/%s/hooks' % self.char_convert(project_id)
        result = self.gitlab_request(url)
        hook_list = []
        if result['status']:
            for hook_info in result['info']:
                hook_list.append({'id': hook_info['id'], 'url': hook_info['url']})
        return hook_list

    def get_gitlab_webhook_info(self, project, hook_id):
        '''
        获取项目某个hook信息,接受完整项目空间或项目id,hook id
        :param project:
        :param hook_id:
        :return:
        '''
        url = '/projects/%s/hooks/%s' % (self.char_convert(project), hook_id)
        result = self.gitlab_request(url)
        return result

    def add_gitlab_webhook(self, project, data):
        '''
        添加hook,接受完整项目空间或项目id,hook属性
        :param project: 项目名或项目id
        :param data: 字典
        :return:
        '''
        url = '/projects/%s/hooks' % self.char_convert(project)
        result = self.gitlab_request(url, data=data)
        return result

    def del_gitlab_webhook(self, project, hook_id):
        result = {
            'status': False
        }
        url = '/projects/%s/hooks/%s' % (project, hook_id)
        delinfo = self.gitlab_request(url, method='DELETE')
        if delinfo['status']:
            result['status'] = True
        else:
            result['message'] = delinfo['message']
        return result


if __name__ == '__main__':
    @click.group()
    def main():
        pass

    @main.command()
    @click.option('--apiroot', '-r', required=True, help='root of gitlab api, like http://***/api/v4')
    @click.option('--token', '-t', required=True, help='private token')
    @click.option('--hook', '-h', required=True, help='url of hook')
    def hook(**options):
        api = GitApi(options['apiroot'], options['token'])
        post_url = options['hook']
        data = {
            'url': post_url,
            'push_events': 'true',
            'tag_push_events': 'true',
            'confidential_issues_events': 'true',
            'note_events': 'true',
            'issues_events': 'true',
            'merge_requests_events': 'true',
            'job_events': 'true',
            'pipeline_events': 'true',
            'wiki_page_events': 'true',
            'token': 'YwRqGxyi-wrEg2hJz-8t'
        }

        project_list = api.get_gitlab_project_list()

        for project in project_list:
            hook_list = api.get_gitlab_webhook_list(project['name'])

            for hook_info in hook_list:
                add_result = {}

                if post_url == hook_info['url']:
                    print '项目[{}]已添加该hook，跳过'.format(project['name'])
                    continue
                else:
                    print '项目[{}]成功添加该hook'.format(project['name'])
                    # add_result = api.add_gitlab_webhook(project['name'], data)

                # if add_result['status']:
                #     print '项目[{}]添加hook成功'.format(project['name'])
                # else:
                #     print '项目[{}]添加hook失败'.format(project['name'])

main()