
# 此文件包含的头文件不要修改
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
from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import requests
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import json

#author 陈宣齐
class SinchewSpider(BaseSpider):
    name = 'sinchew'
    website_id =  13 # 网站的id(必填)
    language_id =  1813 # 所用语言的id
    allowed_domains = ['sinchew.com.my']
    start_urls = ['https://www.sinchew.com.my/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response, **kwargs):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.select('.dropdownlistbylist > a'):
            yield Request(url=i.get('href'),callback=self.parse_2,meta={'category1':i.text})

    def parse_2(self,response):
        page_soup = BeautifulSoup(response.text, 'lxml')
        img = ''
        abstract = ''
        last_time = ''
        if page_soup.find('div', id='articlenum',style='width:670px;text-align:left;float:left;margin-top:30px;') is not None:
            for i in page_soup.select('div #articlenum > li'):
                new_url = i.find('a').get('href')
                title = i.find('div', style='font-size:20px;').text
                abstract = i.find('div', style='font-size:15px;padding-top:5px;').text
                if i.find('img') is not None and i.find('img').get('src') != '/pagespeed_static/1.JiBnMqyl6S.gif':
                    img = i.find('img').get('src')
                pub_time = i.find('div', id='time').text
                last_time = pub_time
                if OldDateUtil.time == None or OldDateUtil.format_time3(pub_time) >= int(OldDateUtil.time):
                    yield scrapy.Request(new_url.strip(),callback=self.parse_3,meta={'category1':response.meta['category1'],'title':title,'pub_time':pub_time,'abstract':abstract,'img':img})
                else:
                    self.logger.info("时间截止")
        if page_soup.find('li', class_='page-next') is not None:
            if OldDateUtil.time == None or OldDateUtil.format_time3(last_time) >= int(OldDateUtil.time):
                yield Request(url=page_soup.find('li', class_='page-next').find('a').get('href').strip(),callback=self.parse_2,meta={'category1':response.meta['category1']})
            else:
                self.logger.info("时间截至")


    def parse_3(self,response):
        new_soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.meta['title']
        item['images'] = [response.meta['img']]
        item['body'] = ''
        for i in new_soup.find('div', id='dirnum').find_all('p'):
            item['body'] += i.text
        if response.meta['abstract'] == '':
            item['abstract'] = item['body'].split('。')[0]
        else:
            item['abstract'] = response.meta['abstract']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item
