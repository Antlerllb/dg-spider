# encoding: utf-8
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy

#author:robot-2233
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

class daSpiderSpider(BaseSpider):
    name = 'da'
    website_id = 1261
    language_id = 1866
    start_urls = ['https://www.da.gov.ph/news/']

    def parse(self,response):
        flag=True
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .post-wrap'):
            ssd=i.select_one(' .post-details').text.strip().split('|')[-1].split()
            if int(ssd[0])<10:
                ssd[0]='0'+str(ssd[0])
            time_ = ssd[-1] + '-' + OldDateUtil.EN_1866_DATE[ssd[1]] + '-' + str(ssd[0]) + ' 00:00:00'
            meta = {'pub_time_': time_}
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                flag=False
                yield Request(url=i.select_one(' .col-md-4 a').get('href'), callback=self.parse_item, meta=meta)
        if flag:
            yield Request(url=soup.select(' .paging a')[2].get('href'), callback=self.parse)


    def parse_item(self, response):
        soup=BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = soup.select_one(' .col-sm-8 h1').text
        item['category1'] = soup.select_one(' #crumbs').text
        item['category2'] = None
        item['body'] = soup.select_one(' article').text.strip()
        item['abstract'] = soup.select(' article p')[0].text
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = soup.select_one(' article img').get('src')
        yield item
