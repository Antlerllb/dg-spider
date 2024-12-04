
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
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

class abscbnSpider(BaseSpider):
    name = 'abs-cbn'
    website_id = 378 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://news.abs-cbn.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }





    def parse(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('.search-container ~ ul > li > a')[1:9]:
            yield Request('https://news.abs-cbn.com'+i.attrs['href'],callback=self.parse2)
        yield Request('https://news.abs-cbn.com/list/tag/tv-patrol',callback=self.parse2)

    def parse3(self, response):
        html = BeautifulSoup(response.text)
        item = NewsItem(language_id=self.language_id)
        list = response.url.split('/')
        item['title'] = html.select('.news-title')[0].text
        item['category1'] = list[3]
        if re.findall(r'\d+',list[4]) == []:
            item['category2'] = list[4]
        item['body'] = ''
        for i in html.select('.article-content > p'):
            item['body'] += (i.text+'\n')
        if html.select('.article-content > p') != []:
            item['abstract'] = html.select('.article-content > p')[0].text
        self.logger.info(html.select('.timestamp-entry > .date-posted')[0].text)
        if html.select('.timestamp-entry > .date-posted') != []:
            item['pub_time'] = OldDateUtil.format_time2(html.select('.timestamp-entry > .date-posted')[0].text)
        else:
            item['pub_time'] = OldDateUtil.format_time()
        if html.select('.article-content > .embed-wrap img') != []:
            item['images'] = [html.select('.article-content > .embed-wrap img')[0].attrs['src'],]
        yield item

    def parse2(self, response):
        html = BeautifulSoup(response.text)
        for i in html.select('.articles > article > a'):
            yield Request('https://news.abs-cbn.com'+i.attrs['href'],callback=self.parse3)
        if html.select('.easyPaginateNav > a[title="Next"]') != [] and (OldDateUtil.time == None or OldDateUtil.format_time3(self.time_format(html.select('.articles > article .datetime')[-1].text)) >= int(OldDateUtil.time)):
            yield Request('https://news.abs-cbn.com'+html.select('.easyPaginateNav > a[title="Next"]')[0].attrs['href'],callback=self.parse2)

    def time_format(self, string):
        list = [i for i in re.split('/| |,|:|\n|\r|\f|\t|\v',string) if i!='']
        return time.strftime("%Y-%m-%d %H:%M:%S", datetime(datetime.now().year,OldDateUtil.month[list[0]],int(list[1]),int(list[2]),int(list[3])).timetuple())