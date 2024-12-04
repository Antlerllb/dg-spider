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

# 经常报403
class siamrathSpider(BaseSpider):
    name = 'siamrath'
    website_id = 1579
    language_id = 2208
    start_urls = ['https://siamrath.co.th/']  # http://www.siamrath.co.th/
    # is_http = 1
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('ul', class_='menu nav navbar-nav').find_all('li')[1:]:
                cate_url = 'https://siamrath.co.th' + i.find('a').get('href')
                category1 = i.find('a').text
                meta1 = {'category1': category1}
                yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta1)
        for i in soup.find('ul', class_='menu nav navbar-nav secondary').find_all('li')[:-1]:
                cate_url = 'https://siamrath.co.th' + i.find('a').get('href')
                category1 = i.find('a').text
                meta1 = {'category1': category1}
                yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta1)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find('div', class_='view-content').find_all('div', class_='col-md-4 col-sm-4 col-xs-6 mb30'):
            title = i.find('h5').text
            images = i.find('a').find('img').get('src')
            t = i.find_all('div')[1].text
            content_url = 'https://siamrath.co.th' + i.find('h5').find('a').get('href')
            year = t.split('/')[2].split(' - ')[0]
            month = t.split('/')[1]
            day = t.split('/')[0].strip(' ')
            clock = t.split('/')[2].split(' - ')[1].strip(' ') + ':00'
            pub_time = year + '-' + month + '-' + day + ' ' + clock
            last_time = pub_time
            meta = {
                'category1': response.meta['category1'],
                'title': title,
                'pub_time': pub_time,
                'images': images
            }
            yield scrapy.Request(content_url, callback=self.parse3, meta=meta)
        if soup.find('ul', class_='pagination').find('li', class_='next') is not None:
            turn_page = 'https://siamrath.co.th' + soup.find('ul', class_='pagination').find('li', class_='next').find('a').get('href')
            if OldDateUtil.time is not None:
                if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield scrapy.Request(url=turn_page, callback=self.parse2, meta=response.meta)
                else:
                    self.logger.info("时间截止")
            else:
                yield scrapy.Request(url=turn_page, callback=self.parse2, meta=response.meta)

    def parse3(self, response, **kwargs):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, features='lxml')
        item['body'] = soup.find('div', class_='field-item even').text.strip()
        item['abstract'] = item['body'].split('.')[0]
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['images'] = response.meta['images']
        yield item
