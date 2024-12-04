
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
class MmmofcomgovcnSpider(BaseSpider):
    name = 'mmmofcomgovcn'
    #allowed_domains = ['http://mm.mofcom.gov.cn/index.shtml']
    start_urls = ['http://mm.mofcom.gov.cn/index.shtml']

    website_id =  1454 # 网站的id(必填)
    language_id =  1813 # 语言  1866 英文

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
        for i in soup.select('.navCon.f-fl a')[1:-1]:
            url='http://mm.mofcom.gov.cn'+i.get('href')
            meta={'category1':i.text}
            yield Request(url=url,callback=self.parse_page,meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        if response.meta['category1'] !='图片专辑':
            last_pub = soup.select_one('.bjgList_01 span').text
            if OldDateUtil.time is None or (OldDateUtil.format_time3(last_pub)) >= int(OldDateUtil.time):
                for i in soup.select('.bjgList_01 li'):
                    try:
                        url='http://mm.mofcom.gov.cn'+i.select_one('a').get('href')
                    except:
                        continue
                    response.meta['title']=i.select_one('a').text
                    response.meta['pub_time']=i.select_one('span').text
                    yield Request(url=url, callback=self.parse_item,meta=response.meta)
            else:
                self.logger.info("时间截止")
                flag = False
        else:
            tt= re.findall('\d{8}',soup.select_one('.pl-detail a').get('href'))[0]
            last_pub="{}-{}-{} 00:00:00".format(tt[:4],tt[4:6],tt[6:])
            if OldDateUtil.time is None or (OldDateUtil.format_time3(last_pub)) >= int(OldDateUtil.time):
                for i in soup.select('.pl-detail a'):
                    url = 'http://mm.mofcom.gov.cn' + i.get('href')
                    response.meta['title'] = i.text
                    tt = re.findall('\d{8}', i.get('href'))[0]
                    pub_time = "{}-{}-{} 00:00:00".format(tt[:4], tt[4:6], tt[6:])
                    response.meta['pub_time'] = pub_time
                    yield Request(url=url, callback=self.parse_item, meta=response.meta)
            else:
                self.logger.info("时间截止")
                flag = False
        if flag:
            try:
                url=response.url+'?'
                currentPage= url.split('?')[1] if url.split('?')[1] != '' else '1'
                nextPage=response.url.split('?')[0]+'?'+str(int(currentPage)+1)
                self.logger.info(nextPage)
                yield Request(url=nextPage, callback=self.parse_page,meta=response.meta)
            except:
                self.logger.info("Next page no more")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['images'] = [i.get('src') for i in soup.select('#zoom img')]
        item['pub_time'] =response.meta['pub_time']
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip() for i in soup.select('#zoom p')])
        item['abstract'] = item['body'].split('\n')[0]
        if item['category1'] == 'Commercial News':
            self.language_id = 1866

        return item