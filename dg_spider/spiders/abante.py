
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

class abanteSpider(BaseSpider):
    name = 'abante'
    website_id = 486 # 网站的id(必填)
    language_id = 1880 # 所用语言的id
    start_urls = ['https://tonite.abante.com.ph/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
        

    def parse(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('#main-navigation > li > a')[:8]:
            yield Request(i.attrs['href'],callback=self.parse2)

    def parse2(self, response):
        html = BeautifulSoup(response.text)
        list = response.url.split('/')
        category1 = list[4]
        for i in html.select('article .title > a'):
            yield Request(i.attrs['href'],meta={'category1':category1},callback=self.parse3)
        if html.select('.older > a') != [] and (OldDateUtil.time == None or OldDateUtil.format_time3(OldDateUtil.format_time2(html.select('article time')[-1].text)) >= int(OldDateUtil.time)):
            yield Request(html.select('.older > a')[0].attrs['href'],callback=self.parse2)

    def parse3(self, response):
        html = BeautifulSoup(response.text)
        item = NewsItem(language_id=self.language_id)
        item['title'] = html.select('.post-title')[0].text
        item['category1'] = response.meta['category1']
        item['body'] = ''
        flag = False
        for i in html.select('div[class="continue-reading-content close"] > p'):
            item['body'] += (i.text+'\n')
            if i.text != '' and flag == False:
                flag = True
                item['abstract'] = i.text
        item['pub_time'] = OldDateUtil.format_time2(html.select('.time > time > b')[0].text)
        if html.select('.single-container .single-featured > img') != []:
            item['images'] = [html.select('.single-container .single-featured > img')[0].attrs['data-src'],]
        yield item
