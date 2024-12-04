
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
from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import socket

class JanoSpider(BaseSpider):
    name = 'janoduniya'
    allowed_domains = ['janoduniya.tv']
    #start_urls = ['http://janoduniya.tv/']
    website_id = 1057  # 网站的id(必填)
    language_id = 1930  # 所用语言的id
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    def start_requests(self):
        socket.setdefaulttimeout(30)
        soup = BeautifulSoup(requests.get('http://janoduniya.tv/').text, 'html.parser')
        for i in soup.select('#primary-menu a')[:-1]:
            meta = {'category1': i.text}
            yield Request(url=i.get('href'), meta=meta)

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        for i in soup.select('article'):
            pub_time = OldDateUtil.format_time2(soup.select_one('.updated').text)
            response.meta['title'] = soup.select_one('h2.entry-title a').text
            response.meta['pub_time'] = pub_time
            if OldDateUtil.time is None or OldDateUtil.format_time3(pub_time) >= int(OldDateUtil.time):
                yield Request(url=i.select_one('a').get('href'), meta=response.meta, callback=self.parse_item)
            else:
                flag = False
                self.logger.info('时间截止')
        if flag:
            try:
                nextPage = soup.select_one('.nav-previous a').get('href')
                yield Request(nextPage, meta=response.meta, callback=self.parse)
            except:
                self.logger.info('Next page no more')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['abstract'] = soup.select_one('.entry-content p').text
        ss = ''
        for i in soup.select('.entry-content p'):
            ss += i.text
        item['body'] = ss
        item['images'] = [i.get('src') for i in soup.select('.np-article-thumb img')]
        item['category2'] = None
        item['pub_time'] = response.meta['pub_time']
        self.logger.info('item item item item item item item item item item item item')
        return item
