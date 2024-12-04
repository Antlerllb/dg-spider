


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

class DiwSpider(BaseSpider):
    name = 'diw'
    website_id = 1728
    language_id = 1898  # 反应较慢
    start_urls = ['https://www.diw.de/de/diw_01.c.620233.de/publikationen/diw_wochenbericht.html?id=diw_01.c.620233.de&von=0']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .teaser_item'):  # 只有年份的时间 只好把月日份都设成了01-01
            time_ = i.select_one(' .teaser_subline').text.split('/')[-1].strip() + '-01-01 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.select_one(' .teaser_header').text.strip(), 'time_': time_,  'category1_': 'Diw'}
                yield Request('https://www.diw.de/'+i.a['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace('.de&von='+response.url.split('.de&von=')[1], '.de&von='+str(int(response.url.split('.de&von=')[1])+20)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        try:  # 有些新闻是pdf要下载
            item['body'] = ''.join([i.text for i in soup.select(' .col-md-10.col-12 p')])
            item['abstract'] = soup.select_one(' .col-md-10.col-12 p').text
            item['pub_time'] = response.meta['time_']
            item['images'] = []
            yield item
        except:
            pass
