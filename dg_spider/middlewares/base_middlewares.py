from typing import Optional

from sqlalchemy.orm import Session

from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.mysql_client import MysqlClient
from scrapy import signals


class MysqlMiddleware:
    def __init__(self):
        self.session: Session = MysqlClient.get_session()

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware._close_mysql, signal=signals.spider_closed)
        return middleware

    def _close_mysql(self, spider: BaseSpider):
        if self.session:
            self.session.close()

class BaseStatsMiddleware(MysqlMiddleware):
    def __init__(self, stats):
        super().__init__()
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.stats)
        crawler.signals.connect(middleware._close_mysql, signal=signals.spider_closed)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_closed(self, spider):
        raise NotImplementedError()

