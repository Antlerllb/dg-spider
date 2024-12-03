import random
from datetime import datetime

from scrapy import Request
from scrapy.exceptions import IgnoreRequest, CloseSpider

from dg_spider.common import USER_AGENT_LIST
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.models import News, Setting
from dg_spider.middlewares.base_middlewares import MysqlMiddleware
from dg_spider.utils.datetime_utils import get_date
from dg_spider.utils.format_utils import str_to_md5, format_log


# 添加请求头
class HeaderMiddlewares:
    def process_request(self, request, spider: BaseSpider):
        ua = random.choice(USER_AGENT_LIST)
        request.headers['User-Agent'] = ua
        return None     # 放行


# URL 查重
class FilterMiddleware(MysqlMiddleware):
    def process_request(self, request: Request, spider: BaseSpider):
        md5 = str_to_md5(request.url)
        result = self.session.query(News).filter(News.md5 == md5).first()
        if result:
            raise IgnoreRequest
        return None     # 放行
