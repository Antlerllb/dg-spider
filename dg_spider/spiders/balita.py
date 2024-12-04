
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
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
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class BalitaSpider(BaseSpider):
    name = 'balita'
    allowed_domains = ['balita.net.ph']
    start_urls = ['http://balita.net.ph/']
    website_id = 195  # 网站的id(必填)
    language_id = 2117  # 所用语言的id
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
          
        

    def parse(self, response):
        if re.match(r'http://balita.net.ph/$', response.url):  # 二级目录
            soup = BeautifulSoup(response.text, 'html.parser')
            for i in soup.select('ul.sub-menu > li > a'):
                url = i.get('href')
                yield scrapy.Request(url, callback=self.parse)
        if re.match(r'http://balita.net.ph/category/', response.url):
            soup = BeautifulSoup(response.text, 'html.parser')
            flag = True
            for i in soup.select('div.tablediv ~ div'):  # 每页的文章
                url = i.select_one('a').get('href')
                pub_time = OldDateUtil.format_time2(i.select_one('.meta_date').text)
                if OldDateUtil.time == None or OldDateUtil.format_time3(pub_time) >= int(OldDateUtil.time):
                    yield scrapy.Request(url, callback=self.parse_item)
                else:
                    flag = False
                    self.logger.info('时间截止')
                    break
            if flag:
                try:
                    nextPage = soup.select_one('span.current ~ a ').get('href')  # 翻页
                    yield scrapy.Request(url=nextPage, callback=self.parse)
                except:
                    self.logger.info(response.url+' has no the next page.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        category = soup.select('span.post_cat > a')[0].text.split('/')
        if len(category) == 1:
            item['category1'] = category
            item['category2'] = None
        else:
            item['category1'] = category[0]
            item['category2'] = category[1]
        item['title'] = soup.select('h1.entry_title')[0].text
        item['pub_time'] = OldDateUtil.format_time2(soup.select('span.post_date')[0].text)
        item['images'] = None
        item['abstract'] = soup.select_one('p').text
        ss = ''
        for i in soup.select('p'):
            ss += i.text + r'\n'
        item['body'] = ss

        yield item
