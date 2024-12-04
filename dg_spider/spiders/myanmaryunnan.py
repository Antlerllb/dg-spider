
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
class MyanmaryunnanSpider(BaseSpider):
    name = 'myanmaryunnan'
    #allowed_domains = ['http://myanmar.yunnangateway.com/html/mobile/mnews/']
    start_urls = ['http://myanmar.yunnangateway.com/html/mobile/mnews/',
                  'http://myanmar.yunnangateway.com/html/mobile/mfinance/',
                  'http://myanmar.yunnangateway.com/html/mobile/mwl/']

    website_id = 1457  # 网站的id(必填)
    language_id =  2065 # 语言
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


    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        last_pub =  soup.select('.list_item_time')[-1].text.split('|')[0][:-1]
        flag = True
        if OldDateUtil.time is None or (OldDateUtil.format_time3(last_pub)) >= int(OldDateUtil.time):
            for i in soup.select('.list_item'):
                meta = {
                    'title': i.select_one('.list_item_title').text,
                    'pub_time': i.select_one('.list_item_time').text.split('|')[0][:-1],
                    'category1': i.select_one('.list_item_chanel').text
                }
                url=i.select_one('.list_item_title a').get('href')
                yield Request(url=url, callback=self.parse_item,meta=meta)
        else:
            self.logger.info("时间截止")
            flag = False
        if flag:
            try:
                nextPage ='http://myanmar.yunnangateway.com'+soup.select_one('#pages>span~a').get('href')
                yield Request(url=nextPage)
            except:
                self.logger.info("Next page no more ")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('.show_con.fl img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('.show_con.fl p')])
        item['abstract'] =item['body'].split('\n')[0]
        return item