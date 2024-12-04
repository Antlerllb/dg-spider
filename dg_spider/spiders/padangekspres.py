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
class padangekspresSpider(BaseSpider):
    name = 'padangekspres'
    website_id = 54
    language_id = 1952
    start_urls = ['http://www.padangekspres.co.id/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find('div',class_='blog-posts').find_all('article',class_='post'):
            if i.find('div',class_='label-line') is not None:
                category1 = i.find('div',class_='label-line').find('a').text
            title = i.find('h2',class_='post-title entry-title').find('a').text
            url = i.find('h2',class_='post-title entry-title').find('a').get('href')
            img = i.find('div',class_='img-thumbnail').find('img').get('data-src')
            abstract = i.find('div',class_='post-snippet').text
            pub_time = i.find('span',class_='time-info').find('time').get('datetime').split('T')[0] + ' 00:00:00'
            meta = {
                'category1':i.find('div', class_='label-line').find('a').text,
                'title':i.find('h2',class_='post-title entry-title').find('a').text,
                'images':i.find('div',class_='img-thumbnail').find('img').get('data-src'),
                'abstract':i.find('div',class_='post-snippet').text,
                'pub_time':i.find('span',class_='time-info').find('time').get('datetime').split('T')[0] + ' 00:00:00'

            }
            last_time = pub_time
            yield scrapy.Request(url, callback=self.parse2, meta=meta)
        for i in soup.find('div', class_='archive-dropdown').find_all('option'):
            if OldDateUtil.time is not None:
                if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield scrapy.Request(url=i.get('value'),callback=self.parse)
                else:
                    self.logger.info("超时啦")
            else:
                yield scrapy.Request(url=i.get('value'), callback=self.parse)

    def parse2(self, response, **kwargs):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, features='lxml')
        item['body'] = soup.find('div',class_='post-body-artikel').text
        item['abstract'] = response.meta['abstract']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['images'] = [response.meta['images']]
        yield item