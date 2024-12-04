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
class SchleswigSpider(BaseSpider):
    name = 'schleswig'
    website_id = 1709
    language_id = 1898
    start_urls = ['https://www.schleswig-holstein.de/DE/landesportal/politik/alle-meldungen/alle-meldungen_node.html']  # 只有一年，全在这页

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .l-content-wrapper .row  .column.small-12'):
            time_ = str(i.time).split('datetime="')[1].split('"')[0]+' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.h2.text.strip('\n'), 'time_': time_, 'category1_': 'politik', 'abstract_': i.p.text.strip() if i.p is not None else '', 'images_': i.img['src']}
                yield Request(i.h2.a['href'], callback=self.parse_item, meta=meat)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .s-richtext.js-richtext').text.strip('\n')
        item['abstract'] = response.meta['abstract_'] if len(response.meta['abstract_']) > 5 else soup.select_one(' .s-richtext.js-richtext p').text
        item['pub_time'] = response.meta['time_']
        item['images'] = [response.meta['images_']]
        yield item
