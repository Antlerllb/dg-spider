from scrapy.http import Request

from dg_spider.libs.models import Website
from dg_spider.middlewares.base_middlewares import MysqlMiddleware


class SpiderOutputMiddleware(MysqlMiddleware):
    def process_spider_output(self, response, result, spider):
        for i in result:
            if isinstance(i, Request):  # 抛出request
                yield i
                continue
            i['request_url'] = response.request.url
            i['response_url'] = response.url
            # i['html'] = response.text
            yield i
