# encoding: utf-8
import random



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# author: robot_2233
Tai_MONTH = {
    'ม.ร.': '01',
    'ก.พ.': '02',
    'มี.น.': '03',
    'เม.ษ.': '04',
    'พ.ค.': '05',
    'มิ.ย.': '06',
    'ก.ค.': '07',
    'ส.ค.': '08',
    'ก.ย.': '09',
    'ต.ค.': '10',
    'พ.ย.': '11',
    'ธ.ค.': '12'}

class banmuangSpider(BaseSpider):
    name = 'banmuang'
    website_id = 233
    language_id = 2208
    start_urls = [f'https://www.banmuang.co.th/news/ajax/{i}/1/2857{str(random.randint(0,200))}:2857{str(random.randint(0,200))}:2857{str(random.randint(0,200))}:2857{str(random.randint(0,200))}' for i in ['politic','crime','economy','property','insure','marketing','it','finance','auto','entertain','education','bangkok','region','social','promotion','gallery','activity']]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .block.list li'):
            ssd = i.span.text.split()
            time_ = str(int(ssd[-1]) - 543) + '-' + Tai_MONTH[ssd[1]] + '-' + (ssd[0] if int(ssd[0]) >= 10 else '0' + ssd[0]) + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'category1_': response.url.split('ajax/')[1].split('/')[0],
                        'title_': i.h4.text,
                        'abstract_': i.p.text,
                        'time_': time_,
                        'images_': i.a.img['src']}
                yield Request(i.a['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            page = response.url.split('/285')[0].split('/')[-1]
            yield Request(response.url.replace('/'+page+'/', '/'+str(int(page)+1)+'/'), meta=meat)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .detail p')])
        item['abstract'] = response.meta['abstract_'].strip()
        item['pub_time'] = response.meta['time_']
        item['images'] = response.meta['images_']
        yield item

