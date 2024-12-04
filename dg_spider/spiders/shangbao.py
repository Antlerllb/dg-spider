
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
import socket

class ShangbaoSpider(BaseSpider):
    name = 'shangbao'
    allowed_domains = ['shangbao.com.ph']
    #start_urls = ['http://www.shangbao.com.ph/']
    website_id = 184  # 网站的id(必填)
    language_id = 2266  # 所用语言的id
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    def start_requests(self):
        socket.setdefaulttimeout(30)
        soup = BeautifulSoup(requests.get('http://www.shangbao.com.ph/').text, 'html.parser')
        for i in soup.select('div #nav_left > a')[1:]:
            url = i.get('href')
            yield scrapy.Request(url, callback=self.parse, meta={'nextpage': 0})

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        for i in soup.select('table '):  # 文章
            url = i.select_one('a').get('href')
            try:
                if OldDateUtil.time == None or OldDateUtil.format_time3(i.select_one('tr').select('td')[-1].text) >= int(OldDateUtil.time):
                    yield scrapy.Request(url, callback=self.parse_item)
                else:
                    flag = False
                    self.logger.info('时间截止')
                    break
            except Exception:
                self.logger.info('Next page no more!')
        if flag:
            url = re.findall('http://s.shangbao.com.ph/es/haiwai/shangbao/[a-z]{4}',response.url)[0] + '?start=' + str(response.meta['nextpage'] * 20)
            response.meta['nextpage'] += 1
            yield scrapy.Request(url, meta=response.meta)

    # def parse_essay(self, response):
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     for i in soup.select('table '):  # 文章
    #         url = i.select_one('a').get('href')
    #         if OldDateUtil.time == None or OldDateUtil.format_time3(i.select_one('tr').select('td')[-1].text) >= int(OldDateUtil.time):
    #             yield scrapy.Request(url, callback=self.parse_item)
    #         else:
    #             self.logger.info('时间截止')

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = soup.select_one('body > div.con > div.con_left > h1').text
        item['category1'] = soup.select('div.dqwz-l > a')[0].text
        try:
            item['category2'] = soup.select('div.dqwz-l > a')[1].text
        except:
            item['category2'] = None
        try:
            item['abstract'] = soup.select_one('#fontzoom > p:nth-child(1) > strong').text
        except:
            item['abstract'] = soup.select_one('#fontzoom > p').text

        ts = soup.select_one('div.left_time').text[0:17]
        time = ts[:4] + '-' + ts[5:7] + '-' + ts[8:10] + ' ' + ts[-5:]
        item['pub_time'] = time
        item['images'] = None

        ss = ""  # strf  body
        for s in soup.select('#fontzoom > p'):
            ss += s.text + r'\n'

        item['body'] = ss

        yield item
