from scrapy import signals
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.format_utils import format_log


class SpiderErrorMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_error, signal=signals.spider_error)
        return middleware

    def spider_error(self, failure, response, spider: BaseSpider):
        spider.logger.error(format_log(self, news_url=response.url, body=failure))

