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

class CsuSpider(BaseSpider):
    name = 'csu'
    website_id = 1714
    language_id = 1898
    start_urls = ['https://www.csu.de/aktuell/meldungen/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .lay-teaser .mod-teaser'):
            ssd = i.select_one(' .m-date').text.strip().split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0].strip('.') + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.select_one(' .m-content').text.strip('\n'), 'time_': time_, 'abstract_': i.select_one(' .js-text').text, 'images_': ['https://www.csu.de/'+i.img['src']]}
                yield Request('https://www.csu.de/'+i.a['href'], callback=self.parse_item, meta=meat)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = 'meldungen'
        item['category2'] = None
        item['body'] = '\n'.join([i.text for i in soup.select(' .m-text p')[1:]])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = response.meta['images_']
        yield item
