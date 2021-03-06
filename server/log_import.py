# coding=utf-8

"""
    webhook_handler.py
"""
from builtins import print

import time
import click
import json
from webhook_handler import dispatch
from web import initialize_db
from web import setup_db_connection
from ga_config import ga_config


@click.group()
def main():
    pass


@main.command()
@click.option('--log-path', '-i', required=True, help='Path of hook log')
@click.option('--gitlab-url', '-u', required=True, help='Url of Gitlab')
@click.option('--private-token', '-k', required=True, help='Private Key')
def event_info(**options):
    ga_config['gitlab_url'] = options['gitlab_url']
    ga_config['private_token'] = options['private_token']
    setup_db_connection()
    initialize_db()

    line_num = 0
    for line in open(options['log_path']):
        line_num += 1

        try:
            data = json.loads(line[0:-1].replace('\n', '\\n'))
            if data['data']['object_kind'] == 'merge_request':
                ret = dispatch(data['data'])
                print("line:{}, ret:{}".format(line_num, ret))
            elif data['data']['object_kind'] == 'note':
                ret = dispatch(data['data'])
                print("line:{}, ret:{}".format(line_num, ret))
            elif data['data']['object_kind'] == 'wiki_page':
                data['data']['timestamp'] = data['timestamp']
                ret = dispatch(data['data'])
                print("line:{}, ret:{}".format(line_num, ret))

                # 模拟不同时间修改，wiki的创建与修改时间没法通过事件和api读取
                time.sleep(1)
            elif data['data']['object_kind'] == 'issue':
                ret = dispatch(data['data'])
                print("line:{}, ret:{}".format(line_num, ret))
            elif data['data']['object_kind'] == 'push':
                ret = dispatch(data['data'])
                print("line:{}, ret:{}".format(line_num, ret))

        except ValueError as e:
            print(e)
            print("line:{} message:{}".format(line_num, line))


if __name__ == '__main__':
    main()
