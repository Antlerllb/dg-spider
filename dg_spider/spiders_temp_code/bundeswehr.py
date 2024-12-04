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
class BundeswehrSpider(BaseSpider): 
    name = 'bundeswehr'
    website_id = 1721
    language_id = 1898
    start_urls = ['https://www.bundeswehr.de/service/bwre/queryListFilter/43250?&limit=8&offset=0']

    def parse(self, response):
        for i in response.json()['items']:
            time_ = i['metaData']['date']['dateTime'] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i['headline'],
                        'time_': time_,
                        'category1_': 'meldungen',
                        'images_': [i['picture']['fallbackSrc']]}
                yield Request(i['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace('&offset=' + response.url.split('&offset=')[1], '&offset=' + str(int(response.url.split('&offset=')[1]) + 1)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = '\n'.join([i.text for i in soup.select(' .c-rte.c-rte--content p')])
        item['abstract'] = soup.select_one(' .c-rte.c-rte--content p').text.strip().strip('\n')
        item['pub_time'] = response.meta['time_']
        item['images'] = response.meta['images_']
        yield item
