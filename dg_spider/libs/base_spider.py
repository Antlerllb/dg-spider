import logging
import os
import signal
import time
from typing import Optional, Any
from twisted.internet import threads
import scrapy
import requests

from dg_spider import my_cfg
from dg_spider.libs.models import Setting, Task
from dg_spider.libs.mysql_client import MysqlClient
from dg_spider.settings import BOT_NAME
from dg_spider.utils.audit_utils import has_json_schema_error
from dg_spider.utils.datetime_utils import get_date
from dg_spider.utils.format_utils import format_log
from dg_spider.utils.io_utils import read_json
from dg_spider.utils.log_utils import setup_log_handler, ScrapyInfoFilter

from dg_spider.libs.models import Website, Audit


class BaseSpider(scrapy.Spider):
    task_id: str = ''
    is_running: bool = True
    args = {}

    def __init__(self, name: Optional[str] = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self._setup_logging()
        self._setup_args(kwargs)
        threads.deferToThread(self._setup_timer)

    @staticmethod
    def _setup_logging():
        logging.getLogger().addFilter(ScrapyInfoFilter())
        console_handler = setup_log_handler(logging.StreamHandler())
        logging.getLogger().addHandler(console_handler)
        for handler in logging.root.handlers:
            handler.addFilter(ScrapyInfoFilter())

    def _setup_args(self, kwargs):
        if kwargs.get('task_id'):
            self.task_id = kwargs.get('task_id')
            with MysqlClient.get_session() as session, session.begin():
                self.args = session.query(Task).filter(Task.id == self.task_id).one().argument
        elif kwargs.get('json_path'):
            self.args = read_json(kwargs.get('json_path'))
        error = has_json_schema_error(self.args, 'spider_args')
        if error:
            self.logger.error(format_log(self, error))
            raise Exception
        display_args = {k: v for k, v in self.args.items() if not k.startswith('_')}
        self.logger.info(format_log(self, f'Start: {display_args}'))

    def _setup_timer(self):
        if self.args['spider']['started_by_scrapy']:
            with MysqlClient.get_session() as session, session.begin():
                timeout_seconds = int(session.query(Setting).filter(Setting.name == 'timeout_seconds').first().value)
                timeout_check_interval = int(session.query(Setting).filter(Setting.name == 'timeout_check_interval').first().value)
            url = '{scrapy_url}/listjobs.json'.format(scrapy_url=my_cfg["scrapy"]["url"])
            while True:
                time.sleep(timeout_check_interval)
                last_scraped_datetime = self.crawler.stats.get_value('last_scraped_datetime')
                if last_scraped_datetime is None:
                    continue
                elapsed_seconds = (get_date() - last_scraped_datetime).total_seconds()
                if elapsed_seconds > timeout_seconds:
                    self.logger.info(format_log(self, f'超过{timeout_seconds}秒未获取新数据，自动关闭爬虫'))
                    if self.args['audit']['enabled']:
                        self.logger.error(format_log(self, '终审不通过'))
                        website_id, audit_id = self.args['spider']['website_id'], self.args['audit']['audit_id']
                        with MysqlClient.get_session() as session, session.begin():
                            website_to_update = session.query(Website).filter(Website.id == website_id).first()
                            audit_to_update = session.query(Audit).filter(Audit.id == audit_id).first()
                            website_to_update.status = 'IN_PROGRESS'
                            audit_to_update.result = 'REJECTED'
                            audit_to_update.audit_time = get_date()
                    running_jobs = requests.get(url).json()['running']
                    for job in running_jobs:
                        if job['id'] == self.task_id:
                            self.logger.info(format_log(self, f'进程已结束：{job["pid"]}'))
                            os.kill(job['pid'], signal.SIGKILL)
                            return
                    raise Exception
