
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
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy

class cebudailynewsSpider(BaseSpider):
    name = 'cebudailynews'
    website_id = 446 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://cebudailynews.inquirer.net/category/breaking',
                'https://cebudailynews.inquirer.net/category/enterprise',
                'https://cebudailynews.inquirer.net/category/nation',
                'https://cebudailynews.inquirer.net/category/world',
                'https://cebudailynews.inquirer.net/category/opinion',
                'https://cebudailynews.inquirer.net/category/sports',
                'https://cebudailynews.inquirer.net/category/life',
                'https://cebudailynews.inquirer.net/category/siloy',
                ]
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
        
        

    def parse(self, response):
        html = BeautifulSoup(response.text)
        list = response.url.split('/')
        if html.select('#cdn-pages-left > div > a') != []:
            for i in html.select('#cdn-pages-left > div#pages-box > a'):
                yield Request(i.attrs['href'],meta={'category1':list[4]},callback=self.parse2)
            if OldDateUtil.time == None or OldDateUtil.format_time3(self.time_format(html.select('#cdn-pages-left > div #postdate-byline > span:nth-of-type(2)')[-1].text)) >= int(OldDateUtil.time):
                yield Request(html.select('#pages-nav > a')[0].attrs['href'])
        else:
            for i in html.select('#cdn-cat-list > div > a'):
                yield Request(i.attrs['href'],meta={'category1':list[4]},callback=self.parse2)
            yield Request(html.select('#list-readmore > a')[-1].attrs['href'])

    def parse2(self, response):
        html = BeautifulSoup(response.text)
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        if response.meta['category1'] != 'life':
            item['title'] = html.select('#landing-headline > h1')[0].text
            item['body'] = ''
            flag = False
            for i in html.select('#article-content > p'):
                item['body'] += i.text
                if i.text != '' and flag == False:
                    flag = True
                    item['abstract'] = i.text
            item['pub_time'] = OldDateUtil.format_time2(html.select('#m-pd2 > span')[-1].text)
            item['images'] = []
            for i in html.select('#article-content img'):
                item['images'].append(i.attrs['src'])
            yield item
        else:
            item['title'] = html.select('#art-hgroup > h1')[0].text
            item['body'] = ''
            flag = False
            for i in html.select('#article-content > p'):
                item['body'] += (i.text+'\n')
                if i.text != '' and flag == False:
                    flag = True
                    item['abstract'] = i.text
            item['pub_time'] = OldDateUtil.format_time2(html.select('.art-byline > span')[-1].text)
            item['images'] = []
            for i in html.select('#article-content img'):
                item['images'].append(i.attrs['src'])
            yield item

    def time_format(self, string):
        list = [i for i in re.split('/| |,|:|\n|\r|\f|\t|\v',string) if i!='']
        return time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(list[2]),int(list[0]),int(list[1])).timetuple())
