# encoding: utf-8




from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re
from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy

ENGLISH_MONTH = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'}

# author:robot-2233  review: 凌敏 pass
class chedSpider(BaseSpider):
    name = 'ched'
    website_id = 1268
    language_id = 1866
    start_urls = ['https://ched.gov.ph/press-releases/']  # 该网站把所有新闻都放在一页里了，不用翻页
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.find_all(style='height: 46px;')[::2]:
            aim_target = i.select_one(' a').get('href')
            i.a.extract()
            sds = ''.join([j for j in i.text.split('\n') if j != ''])
            time_ = sds.split(' ')[2] + '-' + OldDateUtil.EN_1866_DATE[sds.split(' ')[0]] + '-' + sds.split(' ')[1].strip(
                ',') + ' 00:00:00'
            meta = {'pub_time_': time_}
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                if 'pdf' not in aim_target and 'blog' not in aim_target:
                    yield Request(url=aim_target, meta=meta, callback=self.parse_item)
        if OldDateUtil.time is None or 1483113600 >= int(OldDateUtil.time):
            yield Request(url='https://ched.gov.ph/2012-2016-press-releases/', meta=deepcopy(meta),callback=self.Dipper)

    def Dipper(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.find_all(style='height: 46px;')[::2]:
            aim_target = i.select_one(' a').get('href')
            i.a.extract()
            sds = ''.join([j for j in i.text.split('\n') if j != ''])
            time_ = sds.split(' ')[2] + '-' + OldDateUtil.EN_1866_DATE[sds.split(' ')[0]] + '-' + sds.split(' ')[1].strip(
                ',') + ' 00:00:00'
            meta = {'pub_time_': time_}
            if 'pdf' not in aim_target and 'blog' not in aim_target:
                yield Request(url=aim_target, meta=meta, callback=self.parse_item)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = soup.select_one(' .entry-title').text
        item['category1'] = 'News'
        item['category2'] = None
        try:
            item['body'] = ''.join([i.text for i in soup.find_all(dir=re.compile('tr'))])
            if len(item['body']) < 10:
                item['body'] = soup.select_one(' .entry-content').text
        except:
            item['body'] = soup.body.text
        item['abstract'] = ''.join([i.text for i in soup.select(' .entry-content p')[1:4]]) if len(''.join([i.text for i in soup.select(' .entry-content p')[1:4]]))>10 else soup.select_one(' .entry-content').text
        item['pub_time'] = response.meta['pub_time_']
        try:
            item['images'] = soup.find_all(src=re.compile('ched'), id=False)[3].get('src')
        except:
            item['images'] = None
        return item
