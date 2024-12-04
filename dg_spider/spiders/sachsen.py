# encoding: utf-8



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# author: robot_2233
# check:wpf pass
class SachsenSpider(BaseSpider):
    name = 'sachsen'
    website_id = 1708
    language_id = 1898
    start_urls = ['https://www.sachsen-anhalt.de/bs/pressemitteilungen/ministerien/?no_cache=1&tx_tsarssinclude_pi1%5Bpage%5D=1']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .tx-rssdisplay .tx-rssdisplay-newslist'):
            ssd = i.select_one(' .tx-rssdisplay-item-meta-date').text.strip('"').strip().split('"')[0].split('.')
            time_ = ssd[-1].split('/')[1].strip() + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.select_one(' .tx-rssdisplay-item-meta-header').text.strip(),
                        'time_': time_,
                        'category1_': 'ministerien',
                        'abstract_': i.select_one(' .tx-rssdisplay-item-content').text.strip()}
                yield Request(i.a['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace('page%5D=' + response.url.split('page%5D=')[1], 'page%5D=' + str(int(response.url.split('page%5D=')[1]) + 1)), meta=meat)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .tx-rssdisplay-item-content p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = []
        yield item


