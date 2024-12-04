
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

class sunstarSpider(BaseSpider):
    name = 'sunstar'
    website_id = 443 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://www.sunstar.com.ph']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
         
        

    def parse(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('.menu li > a'):
            yield Request(i.attrs['href'],callback=self.parse1)

    def parse1(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('.tablecenter > a')[1:8]:
            yield Request(i.attrs['href'],callback=self.parse2)

    def parse2(self, response):
        html = BeautifulSoup(response.text)
        yield Request(html.select('.row.content > a')[0].attrs['href'],callback=self.parse3)
    
    def parse3(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('.search-inner > div .title > a'):
            yield Request(i.attrs['href'],callback=self.parse_item)
        if OldDateUtil.time == None or OldDateUtil.format_time3(OldDateUtil.format_time2(html.select('.search-inner > div .author span')[-1].text)) >= int(OldDateUtil.time):
            try:
                yield Request(html.select('a.paginationBtn.nextBtn')[0].attrs['href'],callback=self.parse3)
            except Exception:
                pass
        else:
            self.logger.info('截止')

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        html = BeautifulSoup(response.text)
        list = response.url.split('/')
        item['title'] = html.select('.titleArticle > h1')[0].text
        item['category1'] = list[5]
        if re.findall(r'\d+',list[6]) == []:
            item['category2'] = list[6]
        item['body'] = html.select('.col-sm-11 p')[0].text
        item['abstract'] = html.select('.col-sm-11 p')[0].text
        item['pub_time'] = OldDateUtil.format_time2(html.select('.articleDate')[0].text)
        if html.select('.imgArticle > img') != []:
            item['images'] = [html.select('.imgArticle > img')[0].attrs['src'],]
        yield item
