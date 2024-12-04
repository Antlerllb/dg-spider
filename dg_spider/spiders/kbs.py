# encoding: utf-8
import scrapy
import requests
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
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



import re
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil as date

# author:凌敏
# 新闻统一更新，所以发布时间都一样
malay_month = {'Januari': '01', 'Februari': '02', 'Mac': '03', 'April':'04', 'Mei': '05', 'Jun': '06',
'Julai': '07', 'Ogos': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Disember': '12'}

DAY = {'1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06', '7': '07', '8': '08', '9': '09'}

class kbsSpider(BaseSpider):
    name = 'kbs'
    website_id = 397
    language_id = 2036
    start_urls = ['https://www.kbs.gov.my/senarai-berita-kbs']  # http://www.kbs.gov.my
    # is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find('tbody').find_all('tr'):
            title = i.find('td', class_='list-title').find('a').text
            content_url = 'https://www.kbs.gov.my' + i.find('td', class_='list-title').find('a').get('href')
            meta = {'title': title}
            last_time = self.parse3(content_url)
            yield scrapy.Request(url=content_url, callback=self.parse2, meta=meta)
        turn_page = 'https://www.kbs.gov.my' + soup.find('ul', class_='jsn-pagination').find_all('li')[-2].find('a').get('href')
        if OldDateUtil.time is not None:
            if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                yield scrapy.Request(url=turn_page, callback=self.parse)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=turn_page, callback=self.parse)

    def parse2(self, response, **kwargs):
        item = NewsItem(language_id=self.language_id)
        item['body'] = ''
        soup = BeautifulSoup(response.text, features='lxml')
        if soup.find('div', class_='pull-left item-image') is not None:
            item['images'] = 'https://www.kbs.gov.my' + soup.find('div', class_='pull-left item-image').find('img').get('src')
        else:
            item['images'] = []
        item['body'] = soup.find('div', itemprop='articleBody').text
        item['abstract'] = item['body'].split('.')[0]
        item['category1'] = ''
        item['category2'] = ''
        item['title'] = response.meta['title']
        time = soup.find('footer').text.split(':')[-1].strip()
        year = time.split(' ')[2]
        month = malay_month[time.split(' ')[1]]
        day = time.split(' ')[0]
        if int(day) < 10:
            day = DAY[time.split(' ')[0]]
        item['pub_time'] = year+'-'+month+'-'+day+' 00:00:00'
        yield item

    @staticmethod
    def parse3(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features='lxml')
        time = soup.find('footer').text.split(':')[-1].strip()
        year = time.split(' ')[2]
        month = malay_month[time.split(' ')[1]]
        day = DAY[time.split(' ')[0]]
        last_time = year + '-' + month + '-' + day + ' 00:00:00'
        return last_time



