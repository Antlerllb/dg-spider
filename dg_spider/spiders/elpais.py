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
# 每天更新版面，无翻页，无时间截止, 大部分文章需要订阅，所以数据量有点少
class elpaisSpider(BaseSpider):
    name = 'elpais'
    website_id = 1275
    language_id = 2181
    start_urls = ['https://elpais.com']
    # is_http = 1
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find('nav', class_='cs_m').find('div', class_='sm _df').find_all('a'):
            cate_url = 'https://elpais.com'+i.get('href')
            category1 = i.text
            meta1 = {'category1': category1}
            yield scrapy.Request(url=cate_url, callback=self.parse2, meta=meta1)

    def parse2(self, response, **kwargs):
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.find_all('article', class_='c c-d c--m-n'):
            if i.find('h2', class_='c_t').find('a').find('span', class_='c_t_i c_t_i-s _pr') is not None:
                continue  # 需要订阅的内容文章，跳过
            else:
                images = []
                title = i.find('h2', class_='c_t').find('a').text
                content_url = 'https://elpais.com'+i.find('h2', class_='c_t').find('a').get('href')
                meta = {
                    'title': title,
                    'images': images,
                    'category1': response.meta['category1']
                }
                yield scrapy.Request(content_url, callback=self.parse3, meta=meta)
        for i in soup.find_all('article', class_='c c-d c--m'):
            if i.find('h2', class_='c_t').find('a').find('span', class_='c_t_i c_t_i-s _pr') is not None:
                continue  # 需要订阅的内容文章，跳过
            else:
                images = i.find('figure', class_='c_m a_m-h').find('img').get('src')
                title = i.find('h2', class_='c_t').find('a').text
                content_url = 'https://elpais.com'+i.find('h2', class_='c_t').find('a').get('href')
                meta = {
                    'title': title,
                    'images': images,
                    'category1': response.meta['category1']
                }
                yield scrapy.Request(content_url, callback=self.parse3, meta=meta)

    def parse3(self, response, **kwargs):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, features='lxml')
        if soup.find('div', class_='a_md_f').find('time', class_='sg') is None:
            date = soup.find('div', class_='a_md_f').find('time').find('a').get('data-date').split('T')[0]
            time = soup.find('div', class_='a_md_f').find('time').find('a').get('data-date').split('T')[1].split('.')[0]
            if 'Z' in time:
                time = time.split('Z')[0]
            pub_time = date+' '+time
        else:
            date = soup.find('div', class_='a_md_f').find('time', class_='sg').get('data-date').split('T')[0]
            time = soup.find('div', class_='a_md_f').find('time', class_='sg').get('data-date').split('T')[1].split('.')[0]
            if 'Z' in time:
                time = time.split('Z')[0]
            pub_time = date + ' ' + time
        item['body'] = ''
        for i in soup.find('div', class_='a_c clearfix').find_all('p'):
            item['body'] += i.text
        item['abstract'] = item['body'].split('.')[0]
        item['images'] = [response.meta['images']]
        item['title'] = response.meta['title']
        item['pub_time'] = pub_time
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item


