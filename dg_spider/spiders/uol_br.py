# encoding: utf-8
import json

import scrapy
import requests
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

#Author:陈卓玮
class uol_br(BaseSpider):
    name = 'uol_br'
    website_id = 2075
    language_id = 2122
    start_urls = ['https://noticias.uol.com.br/ultimas/']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text)
        for i in soup.select('.flex-wrap > div'):
            try:
                essay_url = (i.select_one('a').get('href'))
                essay_title = (i.select_one('h3').text)
                essay_time = (i.select_one('time').text).split(' ')[0].split('/')[2]+"-"+(i.select_one('time').text).split(' ')[0].split('/')[1]+"-"+(i.select_one('time').text).split(' ')[0].split('/')[0]+" 00:00:00"
                meta = {'essay_title':essay_title,'essay_time':essay_time}
                if 'video' not in essay_url:
                    yield Request(url = essay_url,meta = meta,callback=self.essay_content_parser)
            except:
                pass

        time_stamp = OldDateUtil.str_datetime_to_timestamp(essay_time)
        if OldDateUtil.time == None or OldDateUtil.time <= time_stamp:
            try:
                yield Request(url="https://www.uol.com.br/eleicoes/service/?loadComponent=results-index&data=" + soup.select_one('button').get('data-request'))
            except:
                pass

    def essay_content_parser(self,response):
        soup = BeautifulSoup(response.text)
        img = []
        content=''
        for i in soup.select('p'):
            content+=i.text.strip()+'\n'
        for i in soup.select('img'):
            img.append(i.get('src'))

        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['essay_title']
        item['category1'] = 'news'
        item['body'] = content
        item['abstract'] = content.split('\n')[0]
        item['pub_time'] = response.meta['essay_time']
        item['images'] = img
        yield item

