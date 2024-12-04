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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author: robot_2233
# check:wpf pass
class SachsendeSpider(BaseSpider):
    name = 'sachsende'
    website_id = 1707
    language_id = 1898
    start_urls = [f'https://www.medienservice.sachsen.de/medien/news/search.json?utf8=%E2%9C%93&search%5Bfirst_searched%5D={str(time.strftime("%Y-%m-%d", time.localtime()))}+12%3A25%3A36+UTC&search%5Bquery%5D=&search%5Bfrom%5D=&search%5Bto%5D=&search%5Bfilter%5D%5B%5D=&search%5Bfilter%5D%5B%5D=press_releases&ie-polyfill=&page=1']

    def parse(self, response):
        for i in response.json()['teaser']:
            iii = BeautifulSoup(i, 'html.parser')
            ssd = iii.select_one(' .time').text.strip().split(',')[0].split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            iii.select_one(' .time').extract()
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': iii.select_one(' .teaser-text').text.strip(),
                        'time_': time_,
                        'category1_': 'medien',
                        'images_': 'https://www.medienservice.sachsen.de/'+iii.img['src']}
                yield Request('https://www.medienservice.sachsen.de/'+iii.a['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace('&page=' + response.url.split('&page=')[1], '&page=' + str(int(response.url.split('&page=')[1]) + 1)), meta=meat)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .col p')])
        item['abstract'] = soup.select_one(' .col p').text
        item['pub_time'] = response.meta['time_']
        item['images'] = response.meta['images_']
        yield item


