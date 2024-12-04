import json

from dg_spider.items import NewsItem
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.models import News
from dg_spider.libs.mysql_client import MysqlClient
from dg_spider.pipelines.base_pipelines import MysqlPipeline
from dg_spider.utils.audit_utils import has_json_schema_error
from dg_spider.utils.datetime_utils import get_date
from dg_spider.utils.format_utils import str_to_md5, format_log



class MysqlNewsPipeline(MysqlPipeline):
    def process_item(self, item: NewsItem, spider: BaseSpider):
        if spider.is_running and spider.args['spider']['mysql_enabled'] and isinstance(item, NewsItem):
            error = has_json_schema_error(dict(item), 'news')
            if error:
                spider.logger.error(format_log(self, error, news_url=item['request_url']))
                return None
            item['md5'] = str_to_md5(item['request_url'])
            item['images'] = json.dumps(item['images'])
            item['cole_time'] = get_date().strftime("%Y-%m-%d %H:%M:%S")
            item['website_id'] = spider.args['spider']['website_id']
            with MysqlClient.get_session() as session, session.begin():
                session.add(News(**item))
            spider.crawler.stats.inc_value('run_success_count')
            run_success_count = spider.crawler.stats.get_value('run_success_count')
            spider.logger.info(format_log(self, f'success: {run_success_count}', news_url=item['request_url']))
        return item
