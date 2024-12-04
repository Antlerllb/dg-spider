
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

class entrepreneurSpider(BaseSpider):
    name = 'entrepreneur'
    website_id = 489 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://www.entrepreneur.com/sitemaps/main']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response):
        html = BeautifulSoup(response.text)
        if OldDateUtil.time != None:
            tw = time.localtime(int(OldDateUtil.time))
        for i in html.select('.container > div > div > div:nth-of-type(2) > div'):
            if OldDateUtil.time == None or int(i.select('h2')[0].text) >= tw.tm_year:
                for j in i.select('ul a'):
                    if OldDateUtil.time == None or OldDateUtil.month[j.text.split(' ')[0]] >= tw.tm_mon:
                        yield Request('https://www.entrepreneur.com'+j.attrs['href'],callback=self.parse1)
                    else:
                        break
            else:
                break

    def parse1(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('.nobullet.col3 a'):
            yield Request('https://www.entrepreneur.com'+i.attrs['href'],callback=self.parse2)

    def parse2(self, response):
        item = NewsItem(language_id=self.language_id)
        html = BeautifulSoup(response.text)
        item['title'] = html.select('.headline')[0].text
        if html.select('.valign-wrapper > a') != []:
            item['category1'] = html.select('.valign-wrapper > a')[-1].text
        item['body'] = ''
        flag = False
        for i in html.select('.art-v2-body > div:nth-of-type(1) > p'):
            item['body'] += (i.text+'\n')
            if i.text != '' and flag == False:
                flag = True
                item['abstract'] = i.text
        item['pub_time'] = OldDateUtil.format_time2(html.select('.art-v2-body > div > div > time')[0].text)
        item['images'] = []
        for i in html.select('.art-v2-body > div:nth-of-type(1) img'):
            item['images'].append(i.attrs['src'])
        return item