
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
from dg_spider.utils.old_utils import OldDateUtil as bs
from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class MbSpider(BaseSpider):
    name = 'mb'
    allowed_domains = ['mb.com.ph']
    start_urls = ['https://mb.com.ph']
    website_id = 189  # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    
          
        

    def parse(self, response):
        if re.match(r'https://mb.com.ph$', response.url):  # 匹配一级目录
            soup = bs(response.text, 'html.parser')
            primary_menu = soup.select('#primary-menu > div > ul > li > a')[0:-1]  # 最后一个目录url为None,剃掉
            for i in primary_menu:
                url = i.get('href')
                yield scrapy.Request(url, callback=self.parse)

        elif re.match(r'https://mb.com.ph/\w+/$', response.url):
            soup = bs(response.text, 'html.parser')
            for i in soup.select('#topics-menu > div > ul > li > a'):
                url = i.get('href')
                yield scrapy.Request(url, callback=self.parse)

        elif re.match(r'^https://mb.com.ph/category/', response.url):  # 匹配二级目录下的文章们
            soup = bs(response.text, 'html.parser')
            flag = True
            for i in soup.select('li.article '):
                url = i.select_one('.title a').get('href')

                try:
                    pub_time = i.select_one('time.time-ago').get('data-time')
                except:
                    pass
                if OldDateUtil.time == None or OldDateUtil.format_time3(pub_time) >= int(OldDateUtil.time):
                    yield scrapy.Request(url, callback=self.parse_item ,meta={'pub_time':pub_time})
                else:
                    flag = False
                    self.logger.info('时间截止')
                    break
            if flag:
                nextPage = soup.select_one('.nextpostslink').get('href')
                yield scrapy.Request(nextPage, callback=self.parse)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = bs(response.text, 'html.parser')
        item['title'] = soup.select('div.breadcrumbs > span')[-1].text
        item['category1'] = soup.select('div.breadcrumbs > span')[0].text
        item['category2'] = soup.select('div.breadcrumbs > span')[1].text
        item['abstract'] = soup.select('section.article-content > p')[0].text
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [i.get(' data-cfsrc') for i in soup.select('section.article-content > figure >img')]

        ss = ""  # strf  body
        for s in soup.select('section.article-content > p'):
            ss += s.text + r'\n'

        item['body'] = ss

        yield item
