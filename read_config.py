#!/bin/env python3
# coding: utf-8

import os
from configparser import ConfigParser
from collections import namedtuple

SlackConf = namedtuple("SlackConf", ["api_token","chanel_id"])
GHConf = namedtuple("GH_CONF", ["api_token","github_slack_user_map"])

class Config():
    """A convenience class for reading the config file.
    
    It makes omni-complete work and ensures that things explode early
    if the file does not have any values"""
    def __init__(s):
        conf_file = os.environ.get("STANDUP_CONFIG_FILE",os.path.join(os.path.dirname(os.path.realpath(__file__)),"standup.ini"))
        assert os.path.exists(conf_file), "Could not find config_file: %s"%conf_file

        conf = ConfigParser()
        conf.read(conf_file)

        s.slack = SlackConf( **conf['slack'] ) 
        s.github = GHConf( conf['github']['api_token'], dict(conf["github_slack_user_map"]) ) 

config=Config()
