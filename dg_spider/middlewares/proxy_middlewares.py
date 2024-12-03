import random

from scrapy.exceptions import IgnoreRequest

from dg_spider.libs.base_spider import BaseSpider
from dg_spider.libs.models import Setting
from dg_spider.middlewares.base_middlewares import MysqlMiddleware, BaseStatsMiddleware
from dg_spider.utils.format_utils import format_log


# 实验室代理
class LabProxyMiddleware(MysqlMiddleware):
    is_proxy_invalid = False

    def __init__(self):
        super().__init__()
        self.proxy_generator = self._get_ip()
        self.proxy_list = []

    def _init_proxy_list(self):
        proxy_str = self.session.query(Setting).filter(Setting.name == 'proxy').first().value
        self.proxy_list = proxy_str.split('\n')

    def _get_ip(self):
        while True:
            random.shuffle(self.proxy_list)
            yield from self.proxy_list

    def process_request(self, request, spider: BaseSpider):
        if spider.args['proxy']['enabled'] and spider.args['proxy']['mode'] == 'lab':
            if LabProxyMiddleware.is_proxy_invalid:
                raise IgnoreRequest
            if not self.proxy_list:
                self._init_proxy_list()
                if not self.proxy_list:
                    LabProxyMiddleware.is_proxy_invalid = True
                    spider.logger.error(format_log(self, '代理失效'))
                    raise IgnoreRequest
                else:
                    spider.logger.info(format_log(self, f'加载代理：{self.proxy_list}'))
            request.meta['proxy'] = next(self.proxy_generator)
            return None

# 临时代理
class TempProxyMiddleware:
    def process_request(self, request, spider: BaseSpider):
        if spider.args['proxy']['enabled'] and spider.args['proxy']['mode'] == 'temp':
            temp_proxy = spider.args['proxy']['temp']
            spider.logger.info(format_log(self, f'IP: {temp_proxy["ip"]}'))
            request.meta['proxy'] = f'http://{temp_proxy["ip"]}:{temp_proxy["port"]}'
            return None
