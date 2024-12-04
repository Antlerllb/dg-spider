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
Spanish_MONTH = {'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06', 'julio': '07',
                 'agosto': '08', 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'}


class lapatillaSpider(BaseSpider):
    name = 'lapatilla'
    website_id = 1322
    language_id = 2181
    start_urls = ['https://www.lapatilla.com']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('ul', id='primary-menu').find_all('li')[1:]:
            cate_url = i.find('a').get('href')
            category1 = i.find('a').text
            meta = {'category1': category1}
            yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.find('ul', class_='archive-container').find_all('li'):
            images = i.find('div', class_='row').find('div', class_='post-img-sec').find('a').find('img').get('src')
            title = i.find('div', class_='large-8 medium-8 small-12 description-section column').find('a').find('h4').text
            content_url = i.find('div', class_='large-8 medium-8 small-12 description-section column').find('a').get('href')
            time = i.find('div', class_='large-8 medium-8 small-12 description-section column').find('span', class_='post-date').text
            year = time.split(' ')[4]
            month = Spanish_MONTH[time.split(' ')[2]]
            day = time.split(' ')[3].split(',')[0]
            pub_time = year+'-'+month+'-'+day+' 00:00:00'
            last_time = pub_time
            abstract = i.find('div', class_='large-8 medium-8 small-12 description-section column').find_all('p')[1].text
            meta = {'title': title, 'images': images, 'abstract': abstract,
                    'pub_time': pub_time, 'category1': response.meta['category1']}
            yield scrapy.Request(url=content_url, callback=self.parse3, meta=meta)
        turn_page = soup.find('div', class_='nav-links').find_all('a')[-1].get('href')
        if OldDateUtil.time is not None:
            if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                yield scrapy.Request(url=turn_page, callback=self.parse2, meta=response.meta)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=turn_page, callback=self.parse2, meta=response.meta)

    def parse3(self, response, **kwargs):
        item = NewsItem(language_id=self.language_id)
        item['body'] = ''
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('div', class_='entry-content').find_all('p'):
            item['body'] += i.text
        item['abstract'] = response.meta['abstract']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item
