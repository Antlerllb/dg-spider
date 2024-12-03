import json

from pylint import modify_sys_path
from scrapy.exceptions import DropItem, CloseSpider

from dg_spider.items import NewsItem
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.audit_utils import has_json_schema_error, has_lang_error
from dg_spider.utils.format_utils import format_log



class VerifyNewsPipeline:
    def process_item(self, item: NewsItem, spider: BaseSpider):
        if spider.is_running and not spider.args['spider']['save_to_mysql'] and isinstance(item, NewsItem):
            error = has_json_schema_error(dict(item), 'news')
            if error:
                spider.logger.error(format_log(self, error, news_url=item['request_url']))
                return None
        return item
