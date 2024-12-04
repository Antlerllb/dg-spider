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
from copy import deepcopy

#   Author:叶雨婷
Tai_MONTH = {
        'มกราคม': '01',
        'กุมภาพันธ์': '02',
        'มีนาคม': '03',
        'เมษายน': '04',
        'พฤษภาคม': '05',
        'มิถุนายน': '06',
        'กรกฎาคม': '07',
        'สิงหาคม': '08',
        'กันยายน': '09',
        'ตุลาคม': '10',
        'พฤศจิกายน': '11',
        'ธันวาคม': '12'}

class MoiSpider(BaseSpider):
    name = 'moi'
    allowed_domains = ['moi.go.th']
    start_urls = ['https://www.moi.go.th/moi/category/moi-news/']
    website_id = 1616
    language_id = 2208

    # 翻页拿链接
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        t = soup.select('time')[-1].text.split(' ')
        last_time = str(int(t[2])-543) + "-" + Tai_MONTH[t[1]] + "-" + str(t[0]) + " 00:00:00"
        meta = {'pub_time_': last_time}
        for i in soup.select(' .penci-wrapper-data.penci-grid h2'):
            if 'PDF' in i.a.get('href'):
                pass
            else:
                yield Request(url=i.a.get('href'), callback=self.parse_pages, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            try:
                yield Request(url=soup.select_one('.older a').get('href'), callback=self.parse, meta=deepcopy(meta))
            except AttributeError:
                pass
    # 填表的i
    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = soup.select_one('h1').text
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = "None"
        item['body'] = soup.select_one('p').text
        #print(soup.select_one('p').text)
        item['category1'] = "หน้าแรก"
        item['abstract'] = " "
        item['category2'] = "ข่าวประชาสัมพันธ์"
        yield item




