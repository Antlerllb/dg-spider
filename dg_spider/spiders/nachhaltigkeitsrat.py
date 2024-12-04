


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
class NachhaltigkeitsratSpider(BaseSpider):
    name = 'nachhaltigkeitsrat'
    website_id = 1730
    language_id = 1898
    start_urls = ['https://www.nachhaltigkeitsrat.de/aktuelles/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .post-previews.inner-grid .panel'):
            try:  # 有些不是新闻
                time_ = str(i.time).strip().split('datetime="')[1].split('"')[0].replace('T', ' ').split('+')[0]
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    meat = {'title_': i.h4.text.strip(), 'time_': time_, 'abstract_': i.p.text.strip(), 'category1_': i.select_one(' .category.category-name').text, 'images_': (i.img['src'])}
                    yield Request(i.a['href'], callback=self.parse_item, meta=meat)
            except:
                pass
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if 'seite/' not in response.url:
                yield Request(response.url+'seite/2/')
            else:
                yield Request(response.url.replace('seite/'+response.url.split('seite/')[1], 'seite/'+str(int(response.url.split('seite/')[1].strip('/'))+1)+'/'))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .entry-content p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = [response.meta['images_']]
        yield item
