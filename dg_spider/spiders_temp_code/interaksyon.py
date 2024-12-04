
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
from dg_spider.items import NewsItem
import scrapy
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

class interaksyonSpider(BaseSpider):
    name = 'interaksyon'
    website_id = 490 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://interaksyon.philstar.com/news/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('.td-ss-main-content .td-module-thumb > a'):
            yield Request(i.attrs['href'],callback=self.parse1)
        if OldDateUtil.time == None or OldDateUtil.format_time3(OldDateUtil.format_time2(html.select('.td-ss-main-content > div time')[-1].text)) >= int(OldDateUtil.time):
            yield Request(html.select('.page-nav.td-pb-padding-side > a')[-1].attrs['href'],callback=self.parse)
        
    def parse1(self, response):
        item = NewsItem(language_id=self.language_id)
        html = BeautifulSoup(response.text)
        list = response.url.split('/')
        item['title'] = html.select('.entry-title')[0].text
        item['category1'] = list[3]
        item['body'] = ''
        flag = False
        for i in html.select('.td-post-content.td-pb-padding-side p'):
            item['body'] += (i.text+'\n')
            if i.text != '' and flag == False:
                flag = True
                item['abstract'] = i.text
        item['pub_time'] = OldDateUtil.format_time2(html.select('header > .meta-info')[0].text)
        item['images'] = []
        for i in html.select('.td-post-featured-image img'):
            item['images'].append(i.attrs['src'])
        yield item
