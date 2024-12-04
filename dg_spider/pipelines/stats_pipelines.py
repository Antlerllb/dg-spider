from dg_spider.items import NewsItem
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.models import Setting
from dg_spider.pipelines.base_pipelines import MysqlPipeline
from dg_spider.utils.format_utils import format_log


class StatsPipeline(MysqlPipeline):
    def __init__(self):
        super().__init__()
        self.minimum_news_count = int(self.session.query(Setting).filter(Setting.name == 'minimum_news_count').first().value)

    def process_item(self, item: NewsItem, spider: BaseSpider):
        if spider.is_running and isinstance(item, NewsItem):
            if spider.args['audit']['enabled']:
                spider.crawler.stats.inc_value('audit_success_count')
                audit_success_count = spider.crawler.stats.get_value('audit_success_count')
                spider.logger.info(format_log(self, f'success/require: {audit_success_count}/{self.minimum_news_count}', news_url=item['request_url']))
            else:
                spider.crawler.stats.inc_value('run_success_count')
                audit_success_count = spider.crawler.stats.get_value('run_success_count')
                spider.logger.info(format_log(self, f'success: {audit_success_count}', news_url=item['request_url']))
        return item
