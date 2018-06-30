# coding=utf-8

"""
    utils.py
"""
import os
import ConfigParser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_config(section, option):
    """ fetch config from config.ini """
    parser = ConfigParser.ConfigParser()
    conf_file = os.path.join(BASE_DIR, 'config.ini')
    try:
        parser.read(conf_file)
        return parser.get(section, option)
    except:
        raise Exception('Open {} failed'.format(conf_file))


