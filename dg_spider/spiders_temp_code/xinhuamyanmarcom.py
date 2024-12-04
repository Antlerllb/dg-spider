
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
from scrapy import FormRequest
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
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
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# author 刘鼎谦
class XinhuamyanmarcomSpider(BaseSpider):
    name = 'xinhuamyanmarcom'
    #allowed_domains = ['https://xinhuamyanmar.com/']
    start_urls = ['https://xinhuamyanmar.com/']

    website_id = 1459  # 网站的id(必填)
    language_id = 2065  # 语言
    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'local_crawler',
    #     'password': 'local_crawler',
    #     'db': 'local_dg_test'
    # }
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    timesAgo=['months','years','month','year']

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-main-menu > li > a')[1:]:
            meta={'category1':i.text}
            yield Request(url=i.get('href'),callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        tt=soup.select('.mvp-blog-story-list.left.relative.infinite-content .mvp-cd-date.left.relative')[0].text
        if tt.split()[1] in self.timesAgo:
            flag=False
            last_pub = '1991-03-10 00:00:00'
        else:
            last_pub = OldDateUtil.format_time2(tt)
        if OldDateUtil.time is None or (OldDateUtil.format_time3(last_pub)) >= int(OldDateUtil.time):
            self.logger.info(response.url)
            self.logger.info(tt)
            for i in soup.select('.mvp-blog-story-wrap.left.relative.infinite-post'):
                response.meta['title']= i.select_one('h2').text
                response.meta['pub_time']=OldDateUtil.format_time2(i.select_one('.mvp-cd-date.left.relative').text.strip())
                url=i.select_one('a').get('href')
                yield Request(url=url, callback=self.parse_item,meta=response.meta)
        else:
            self.logger.info("时间截止")
            self.logger.info(response.url)
            flag = False
        if flag:
            try:
                url=response.url+'page'
                if url.split('page')[1] == '':
                    currentPage='1'
                else:
                    currentPage=response.url.split('page')[1][1:-1]
                nextPage=response.url.split('page')[0]+f"page/{str(int(currentPage)+1)}/"
                yield Request(url=nextPage, callback=self.parse_page,meta=response.meta)
            except:
                self.logger.info("Next page no more ")


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('#mvp-post-feat-img img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('#mvp-content-main p')])
        item['abstract'] = item['body'].split('\n')[1]
        return item