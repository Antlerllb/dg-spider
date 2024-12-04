
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
class MyitkyinanewsjournalSpider(BaseSpider):
    name = 'myitkyinanewsjournal'
    # allowed_domains = ['https://www.myitkyinanewsjournal.com/']
    start_urls = ['https://www.myitkyinanewsjournal.com/']

    website_id =  1490 # 网站的id(必填)
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

    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-mknj-main-menu-1 a')[2:-4]:
            meta={'category1':i.text.strip()}
            url=i.get('href')
            yield Request(url=url, callback=self.parse_page,meta=meta)


    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        last_pub = soup.select('.td-block-span6 time')[-1].get('datetime').replace('T',' ')[:-6]
        flag=True
        if OldDateUtil.time is None or (OldDateUtil.format_time3(last_pub)) >= int(OldDateUtil.time):
            for i in soup.select('.td-block-span6'):
                url=i.select_one('a').get('href')
                response.meta['title']=i.select_one('h3').text
                response.meta['pub_time']=i.select_one('time').get('datetime').replace('T',' ')[:-6]
                yield Request(url=url, callback=self.parse_item,meta=response.meta)
        else:
            self.logger.info("时间截止")
            flag = False
        if flag:
            try:
                currentPage=1 if len(response.url.split('page')) == 1 else int(re.findall('\d+',response.url)[0])
                nextPage=response.url.split('page')[0]+"page/{}/".format(str(currentPage+1))
                yield Request(url=nextPage, callback=self.parse_page,meta=response.meta)
            except:
                self.logger.info("Next page no more ")


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('.td-post-featured-image img')]
        item['pub_time'] = response.meta['pub_time']
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select(".td-post-content.tagdiv-type p")])
        item['abstract'] = item['body'].split('\n')[1]
        return item