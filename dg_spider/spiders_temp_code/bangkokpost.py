from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from datetime import date



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re

ENGLISH_MONTH = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'}

class bangkokpostSpider(BaseSpider):  # author：田宇甲  review: 凌敏  pass
    name = 'bangkokpost'  # 这个网站十分小气，它的规模不小但是新闻只给获取到一个月内的，应该是那边的后台写了时间检查，如果时间太久就不返回给前端
    website_id = 224
    language_id = 1866
    start_urls = ['https://www.bangkokpost.com/list_content/world?page=1',
                  'https://www.bangkokpost.com/list_content/thailand?page=1',
                  'https://www.bangkokpost.com/list_content/business?page=1',
                  'https://www.bangkokpost.com/list_content/opinion?page=1',
                  'https://www.bangkokpost.com/list_content/auto?page=1',
                  'https://www.bangkokpost.com/list_content/life?page=1',
                  'https://www.bangkokpost.com/list_content/asiafocus?page=1']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.find_all(class_=re.compile('listnews-row')):
            ssd = i.select_one(' .listnews-datetime').text.split()
            if len(ssd) > 1:  # 正常的时间处理
                time_ = ssd[-1] + '-' + OldDateUtil.EN_1866_DATE[ssd[1]] + '-' + str(ssd[0]) + ' 00:00:00'
            else:  # 异常的时间处理
                time_ = str(date.today()) + ' ' + ssd[0] + ':00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_, 'title_': i.h3.a.text, 'abstract_': i.p.text, 'images_': 'https://www.bangkokpost.com/'+i.select_one(' .listnews-img a img')['src'] if i.select_one(' .listnews-img') is not None else None, 'category1_': response.url.split('list_content/')[1].split('?')[0]}
                yield Request('https://www.bangkokpost.com/'+i.h3.a['href'], callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace(response.url.split('page=')[1], str(int(response.url.split('page=')[1])+1)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = '\n'.join([i.text for i in soup.select(' .articl-content p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
