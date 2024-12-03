from dg_spider.libs.mysql_client import MysqlClient
from scrapy import signals


class MysqlMiddleware:
    def __init__(self):
        self.session = MysqlClient.get_session()


class BaseStatsMiddleware(MysqlMiddleware):
    def __init__(self, stats):
        super(BaseStatsMiddleware, self).__init__()
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.stats)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_closed(self, spider):
        raise NotImplementedError()

