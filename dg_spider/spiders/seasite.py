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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author:凌敏
class seasiteSpider(BaseSpider):
    name = 'seasite'
    website_id = 60
    language_id = 1866
    start_urls = ['http://www.seasite.niu.edu/Indonesian/']
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        con_urls = 'http://www.seasite.niu.edu/Indonesian/'
        category1 = soup.find('ul',id='drop-nav').find_all('li')[1].find_all('a')[0].text
        for i in soup.find('ul',id='drop-nav').find_all('li')[1].find('ul').find_all('li'):
            if i.find('a').get('href') != '#' and i.find('a').get('href') != 'new_indonesian/tatabahasa/index.html':
                url = con_urls + i.find('a').get('href')
                category2 = i.find('a').text
                meta={'category1':category1, 'category2':category2, 'url':url}
                yield scrapy.Request(url,callback=self.parse1,meta=meta)

    def parse1(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = time.strftime("%Y-%m-%d %H:%M:%S")
        title = soup.find('div',class_='section-title text-left').find('h2').text
        body = soup.find_all('div',class_='container')[2].text
        for i in soup.find_all('div',class_='container')[2].find_all('a'):
            url = response.meta['url'].split('index.html')[0] + i.get('href')
            meta = {'title':title, 'body':body, 'category1':response.meta['category1'],
                    'category2':response.meta['category2']}
            yield scrapy.Request(url,callback=self.parse2,meta=meta)
        if OldDateUtil.time is not None:
            if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                yield scrapy.Request(url=url, callback=self.parse1)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=url, callback=self.parse1)

    def parse2(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, features='lxml')
        if soup.find_all('div',class_='container')[2].text is not None:
            item['body'] = soup.find_all('div',class_='container')[2].text
            item['abstract'] = soup.find_all('div',class_='container')[2].text.split('.')[0]
        else:
            item['body'] = response.meta['body']
            item['abstract'] = response.meta['body'].split('.')[0]
        item['title'] = response.meta['title']
        item['pub_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        item['images'] = []
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        yield item

