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
class RegierungSpider(BaseSpider):
    name = 'regierung'
    website_id = 1702
    language_id = 1898
    start_urls = ['https://www.regierung-mv.de/Aktuell/?pager.page.nr=0&pager.items.offset=0']
    page = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .resultlist .teaser'):
            ssd = i.select_one(' .dtstart').text.strip().split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.h3.text.strip(), 'time_': time_, 'category1_': i.select_one(' .ressort-name-short').text, 'abstract_': i.p.text.strip()}
                yield Request('https://www.regierung-mv.de/'+i.h3.a['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request(f'https://www.regierung-mv.de/Aktuell/?pager.page.nr={str(RegierungSpider.page)}&pager.items.offset={str(RegierungSpider.page*10)}')
            RegierungSpider.page += 1

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .absatz p')[0:-1]])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = []
        yield item
