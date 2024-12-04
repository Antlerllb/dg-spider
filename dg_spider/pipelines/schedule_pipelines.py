from datetime import datetime
from scrapy.exceptions import CloseSpider

from dg_spider.items import NewsItem
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.models import Setting
from dg_spider.middlewares.base_middlewares import MysqlMiddleware
from dg_spider.utils.datetime_utils import str_to_datetime, get_date
from dg_spider.utils.format_utils import format_log


class MaxItemsStopMiddleware(MysqlMiddleware):
    def __init__(self):
        super().__init__()
        self.minimum_news_count = int(self.session.query(Setting).filter(Setting.name == 'minimum_news_count').first().value)

    def process_item(self, item: NewsItem, spider: BaseSpider):
        if spider.is_running and spider.args['audit']['enabled'] and isinstance(item, NewsItem):
            audit_success_count = spider.crawler.stats.get_value('audit_success_count')
            if audit_success_count > self.minimum_news_count:
                spider.logger.info(format_log(self, f'新闻量已达到{self.minimum_news_count}，停止中'))
                spider.crawler.engine.close_spider(spider)
                spider.is_running = False
        return item


class TimePointStopMiddleware:
    def process_item(self, item: NewsItem, spider: BaseSpider):
        if spider.is_running and spider.args['timer']['enabled'] and isinstance(item, NewsItem):
            crawl_until_datetime = datetime.fromisoformat(spider.args['timer']['crawl_until_datetime'])
            if str_to_datetime(item['pub_time']) < crawl_until_datetime:
                spider.logger.info(format_log(self, f'增量式爬虫结束：{crawl_until_datetime}'))
                spider.is_running = False
                spider.crawler.engine.close_spider(spider)
        return item


class ShutdownPipeline:
    def process_item(self, item: NewsItem, spider: BaseSpider):
        if not spider.is_running:
            spider.logger.info(format_log(self, '正在清空请求队列'))
        return item

