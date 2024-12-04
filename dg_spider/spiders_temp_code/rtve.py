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
class rtveSpider(BaseSpider):
    name = 'rtve'
    website_id = 1280
    language_id = 2181
    start_urls = ['http://www.rtve.es']
    # is_http = 1
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        cate = soup.select('.blindBox > .maintabs > li')[3:7]
        for i in cate:
            cate_url = i.find('a').get('href')
            category1 = i.find('a').get('title')
            meta1 = {'category1': category1}
            yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta1)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find_all('article', class_='cell'):
            content_url = i.find('div', class_='txtBox').find('a').get('href')
            if content_url.split('/')[4] == 'videos':  # 内容为视频
                continue
            title = i.find('span', class_='maintitle').text
            meta = {
                'title': title,
                'category1': response.meta['category1']
            }
            if OldDateUtil.time is not None:
                last_time = self.parse4(content_url)
                if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield scrapy.Request(content_url, callback=self.parse3, meta=meta)
                else:
                    self.logger.info("时间截止")
            else:
                yield scrapy.Request(content_url, callback=self.parse3, meta=meta)

    def parse3(self, response, **kwargs):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, features='lxml')
        if response.url.split('/')[4] == 'audios':
            t = soup.find('span', class_='pubBox').find('span', class_='datemi').text
            year = t.split('/')[2]
            month = t.split('/')[1]
            day = t.split('/')[0]
            item['pub_time'] = year+'-'+month+'-'+day+' 00:00:00'
            item['images'] = soup.find('span', class_='ima').find('img').get('src')
            item['body'] = ''
            for i in soup.find('div', class_='mainDescription').find_all('p'):
                item['body'] += i.text.strip()
            item['abstract'] = item['body'].split('.')[0]
        else:
            date = soup.find('p', class_='pubBox').find('time').get('datetime').split('T')[0]
            time = soup.find('p', class_='pubBox').find('time').get('datetime').split('T')[1].split('+')[0]
            item['pub_time'] = date+' '+time
            item['images'] = soup.find('span', class_='ima T H f16x9').find('img').get('src')
            item['body'] = ''
            for i in soup.find('div', class_='mainContent hid_email').find_all('p'):
                item['body'] += i.text.strip()
            item['abstract'] = item['body'].split('.')[0]
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item

    @staticmethod
    def parse4(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features='lxml')
        if url.split('/')[4] == 'audios':
            t = soup.find('span', class_='pubBox').find('span', class_='datemi').text
            year = t.split('/')[2]
            month = t.split('/')[1]
            day = t.split('/')[0]
            last_time = year+'-'+month+'-'+day+' 00:00:00'
        else:
            date = soup.find('p', class_='pubBox').find('time').get('datetime').split('T')[0]
            time = soup.find('p', class_='pubBox').find('time').get('datetime').split('T')[1].split('+')[0]
            last_time = date + ' ' + time
        return last_time

