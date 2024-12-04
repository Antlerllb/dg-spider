from scrapy import signals

from dg_spider.libs.base_spider import BaseSpider
from dg_spider.middlewares.base_middlewares import BaseStatsMiddleware
from dg_spider.utils.format_utils import format_log


class StatsInitMiddleware:
    def __init__(self, stats):
        self.run_stats = {
            'run_success_count': 0,
        }
        self.audit_stats = {
            'is_audit_passed': True,
            'audit_success_count': 0,
            'audit_item_error_count': 0,
            'audit_lang_error_count': 0,
            'audit_lang_total_count': 0,
        }

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls(crawler.stats)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider: BaseSpider):
        stats_to_update = self.run_stats
        if spider.args['audit']['enabled']:
            stats_to_update.update(self.audit_stats)
        for key, value in stats_to_update.items():
            spider.crawler.stats.set_value(key, value)


class ArgsSummaryMiddleware(BaseStatsMiddleware):
    def spider_closed(self, spider):
        spider.logger.info(format_log(self, 'Close', body=spider.args))

