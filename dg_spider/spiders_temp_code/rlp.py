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
class RlpSpider(BaseSpider):
    name = 'rlp'
    website_id = 1705
    language_id = 1898
    start_urls = ['https://www.rlp.de/de/service/pressemeldungen/seite/1/']
    page = 2

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .news-list-content-view .row .small-12.columns article'):
            ssd = i.select_one(' .news-list-date').text.strip().split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.h4.text.strip(), 'time_': time_, 'category1_': 'pressemeldungen', 'abstract_': i.select_one(' .teaser-text').text.strip()}
                yield Request('https://www.rlp.de/'+i.h4.a['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request('https://www.rlp.de/de/service/pressemeldungen/seite/'+str(RlpSpider.page)+'/')
            RlpSpider.page += 1

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .news-text-wrap').text
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = []
        yield item
