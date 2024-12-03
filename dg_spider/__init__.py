import importlib.resources as pkg_resources
import logging
import os
import yaml
from scrapy.utils.log import configure_logging
from twisted.internet import asyncioreactor
from dg_spider.settings import LOGGING

# 读取yaml配置
with pkg_resources.path('dg_spider.resources.config', 'config.yaml') as datafile:
    with open(datafile, 'r', encoding='utf-8') as f:
        my_yaml = yaml.safe_load(f)
        my_cfg = my_yaml['default']
        env = os.getenv('MY_ENV', 'dev')
        my_cfg.update(my_yaml[env])

# 异步开启子进程
asyncioreactor.install()

# 禁用scrapy日志
configure_logging(install_root_handler=False)
logging.config.dictConfig(LOGGING)

