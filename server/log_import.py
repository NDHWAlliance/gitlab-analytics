# coding=utf-8

"""
    webhook_handler.py
"""
from builtins import print

import time
import click
import json
from urllib import request
from utils import get_config
from webhook_handler import dispatch
from gitlab_analytics_models import *


@click.group()
def main():
    pass


@main.command()
@click.option('--log-path', '-i', required=True, help='Path of hook log')
def event_info(**options):
    # 查看下当前可以统计的事件
    # 删除表重新来哦

    hook_host = get_config('hook', 'host')
    hook_port = get_config('hook', 'port')
    req_url = "http://{}:{}/web_hook/".format(hook_host, hook_port)

    line_num = 0
    for line in open(options['log_path']):
        line_num += 1

        try:
            data = json.loads(line[0:-1].replace('\n', '\\n'))
            if data['data']['object_kind'] == 'wiki_page':
                # req = request.Request(req_url)
                # ret = request.urlopen(req, bytes(json.dumps(data['data']), 'utf8')).read()
                ret = dispatch(data['data'])
                print("line:{}, ret:{}".format(line_num, ret))
                time.sleep(1)
        except ValueError as e:
            print(e)
            print("line:{} message:{}".format(line_num, line))


if __name__ == '__main__':
    main()
