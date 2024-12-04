#
# encoding: utf-8
import copy
import json

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


# from crawler.spiders.dynamicutusan import p_time

from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import requests
import datetime

time_dict = {'Januari': '01', 'Februari': '02', 'Mac': '03', 'April': '04', 'Mei': '05', 'Jun': '06', 'Julai': '07',
             'Ogos': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Disember': '12', 'pm': 12, 'am': 0}

def p_time(pt):

    time_list = pt.split('/')  # %Y-%m-%d %H:%M:%S
    time_ = "{}-{}-{} {}:{}:{}".format(time_list[2], time_list[1], time_list[0], '00',
                                           '00', "00")
    return time_
# author: 华上瑛

class ChannelnewsasiaSpider(BaseSpider):
    name = 'channelnewsasia'
    website_id = 457
    language_id = 1866
    start_urls = ['https://www.channelnewsasia.com/singapore',
                  'https://www.channelnewsasia.com/asia','https://www.channelnewsasia.com/world',
                  'https://www.channelnewsasia.com/commentary','https://www.channelnewsasia.com/sport',
                  'https://www.channelnewsasia.com/coronavirus-covid-19','https://www.channelnewsasia.com/business',
                  'https://www.channelnewsasia.com/sustainability'] # 'https://www.kosmo.com.my/terkini/',
    post_url = ''

    params = {
        'page': '1',
        '_format': 'json',
        'viewMode': 'infinite_scroll_listing'
    }
    page = {'singapore': '0', 'asia': '0', 'coronavirus-covid-19': '0', 'sport': '0',
            'business': '0', 'commentary': '0', 'world': '0','sustainability':'0'}
    proxy = '02'

    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD' :"TLSv1.2",'RETRY_TIMES':10,'DOWNLOAD_DELAY':0.1,'RANDOMIZE_DOWNLOAD_DELAY':True}

    def start_requests(self):
        for i in self.start_urls:
            yield Request(url=i,callback=self.parse)

    def parse(self, response):
        try:
            if 'api' in response.url:
                soup1 = json.loads(response.text)
                category1 = copy.deepcopy(response.meta['category1'])
                articles = soup1["result"]

                flag = True
                last_time = datetime.datetime.strptime(soup1["result"][-1]['release_date'].split('+0800')[0].replace('T'," "),"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=int(8))
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
                    for article in articles:
                        news_url = article['absolute_url']
                        pub_time = datetime.datetime.strptime(article['release_date'].split('+0800')[0].replace('T'," "),"%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=int(8))
                        title = article['title']
                        img = [article['image_url']]
                        yield Request(url=news_url, callback=self.parse_item,
                                      meta={'category1': category1, 'pub_time': pub_time, 'images': img,
                                            'title': title}, dont_filter=True)
                else:
                    flag = False
                    self.logger.info("时间截止")

            else:
                soup = BeautifulSoup(response.text,'html.parser')
                category1 = copy.deepcopy(response.url.split('/')[-1].strip())
                articles = soup.select('div.grid-cards-four-column.grid-card-carousel-mobile > div.card-object')

                flag = True
                l_time = articles[-1].select('div > div > div > div > span')[0].text.strip()
                last_time = p_time(l_time)
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
                    for article in articles:
                        news_url = 'https://www.channelnewsasia.com'+article.select('div > div > div > h6 > a')[0].get('href')
                        pub_time = p_time(article.select('div > div > div > div > span')[0].text.strip())
                        title = article.select('div > div > div > h6 > a')[0].text.strip()
                        img = [article.select('div > a > picture > img')[0].get('src')]
                        yield Request(url=news_url, callback= self.parse_item, meta={'category1':category1,'pub_time':pub_time,'images':img,'title':title},dont_filter=True)
                else:
                    flag = False
                    self.logger.info("时间截止")

            if flag:  # 翻页post
                if category1 == 'singapore':
                    self.page['singapore'] = str(int(self.page['singapore']) + 1)
                    self.params['page'] = str(self.page['singapore'])
                    post_url_ = 'https://www.channelnewsasia.com/api/v1/infinitelisting/94f7cd75-c28b-4c0a-8d21-09c6ba3dd3fc?_format=json&viewMode=infinite_scroll_listing&page='
                    self.post_url = post_url_ + self.page['singapore']

                    yield scrapy.FormRequest(url=self.post_url, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'asia':
                    self.page['singapore'] = str(int(self.page['singapore']) + 1)
                    self.params['page'] = str(self.page['singapore'])
                    post_url_ = 'https://www.channelnewsasia.com/api/v1/infinitelisting/1da7e932-70b3-4a2e-891f-88f7dd72c9d6?_format=json&viewMode=infinite_scroll_listing&page='
                    self.post_url = post_url_ + self.page['singapore']

                    yield scrapy.FormRequest(url=self.post_url, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'world':
                    self.page['world'] = str(int(self.page['world']) + 1)
                    self.params['page'] = str(self.page['world'])
                    post_url_ = 'https://www.channelnewsasia.com/api/v1/infinitelisting/9f7462b9-d170-42c1-a26c-5f89720ff5c9?_format=json&viewMode=infinite_scroll_listing&page='
                    self.post_url = post_url_ + self.page['world']

                    yield scrapy.FormRequest(url=self.post_url, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'commentary':
                    self.page['commentary'] = str(int(self.page['commentary']) + 1)
                    self.params['page'] = str(self.page['commentary'])
                    post_url_ = 'https://www.channelnewsasia.com/api/v1/infinitelisting/f8f0f8b1-004c-486f-ac72-0c927b7b539d?_format=json&viewMode=infinite_scroll_listing&page='
                    self.post_url = post_url_ + self.page['commentary']

                    yield scrapy.FormRequest(url=self.post_url, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)

                elif category1 == 'sustainability':
                    self.page['sustainability'] = str(int(self.page['sustainability']) + 1)
                    self.params['page'] = str(self.page['sustainability'])
                    post_url_ = 'https://www.channelnewsasia.com/api/v1/infinitelisting/8c987d96-e7f0-42ef-8629-0ffd6e02db6d?_format=json&viewMode=infinite_scroll_listing&page='
                    self.post_url = post_url_ + self.page['sustainability']

                    yield scrapy.FormRequest(url=self.post_url, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)

                elif category1 == 'business':
                    self.page['business'] = str(int(self.page['business']) + 1)
                    self.params['page'] = str(self.page['business'])
                    post_url_ = 'https://www.channelnewsasia.com/api/v1/infinitelisting/5207efc4-baf1-47a8-a6d3-47a940cc115c?_format=json&viewMode=infinite_scroll_listing&page='
                    self.post_url = post_url_ + self.page['business']

                    yield scrapy.FormRequest(url=self.post_url, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)

                elif category1 == 'sport':
                    self.page['sport'] = str(int(self.page['sport']) + 1)
                    self.params['page'] = str(self.page['sport'])
                    post_url_ = 'https://www.channelnewsasia.com/api/v1/infinitelisting/da22669b-311e-4347-8bd9-6cdbcec9c380?_format=json&viewMode=infinite_scroll_listing&page='
                    self.post_url = post_url_ + self.page['sport']

                    yield scrapy.FormRequest(url=self.post_url, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)

                elif category1 == 'coronavirus-covid-19':
                    self.page['coronavirus-covid-19'] = str(int(self.page['coronavirus-covid-19']) + 1)
                    self.params['page'] = str(self.page['coronavirus-covid-19'])
                    post_url_ = 'https://www.channelnewsasia.com/api/v1/infinitelisting/ddeeb87a-fa8d-4ae7-a685-f4ff13b0ddfb?_format=json&viewMode=infinite_scroll_listing&page='
                    self.post_url = post_url_ + self.page['coronavirus-covid-19']

                    yield scrapy.FormRequest(url=self.post_url, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
        except:
            self.logger.info("no more pages")


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        content = soup.select('div.text-long > p')
        body = " "
        for b in content:
            body += b.text.strip()
        try:
            abstract = soup.select('div.content-detail__description > p')[0].text.strip()
        except:
            abstract = body.split('.')[0]

        item['category1'] = response.meta['category1']
        item['category2'] = ""
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        item['body'] = body
        item['abstract'] = abstract

        yield item




