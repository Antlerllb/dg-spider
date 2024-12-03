import importlib.resources as pkg_resources
import os
import yaml
from twisted.internet import asyncioreactor


with pkg_resources.path('dg_spider.resources.config', 'config.yaml') as datafile:
    with open(datafile, 'r', encoding='utf-8') as f:
        my_yaml = yaml.safe_load(f)
        my_cfg = my_yaml['default']
        env = os.getenv('MY_ENV', 'dev')
        my_cfg.update(my_yaml[env])


asyncioreactor.install()
