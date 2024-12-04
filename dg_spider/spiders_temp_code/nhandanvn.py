
# encoding: utf-8




from scrapy.http.request import Request
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
#author: robot_2233

class nhandanSpiderSpider(BaseSpider):
    name = 'nhandan.vn'
    website_id = 2048
    language_id = 2242 # 越南语
    #本爬虫实验性直接请求了网站源码,有意思
    start_urls = [f'https://nhandan.vn/article/Paging?categoryId={i}&pageIndex=1&pageSize=50&fromDate=&toDate=&displayView=PagingPartial' for i in ['1251','1171','1185','1211','1287','1257','1231','1224','1303','1309','1292','1296','1315']]


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' article'):
            ssd = i.select_one(' .box-meta-small').text.split(' ')
            time_ = ssd[1].split('/')[-1] + '-' + ssd[1].split('/')[1] + '-' + ssd[1].split('/')[0] + ' ' + ssd[0] + ':00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_}
                yield Request(url='https://nhandan.vn'+i.select_one(' .box-title').a.get('href'),  callback=self.parse_item,meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            tyj=str(response.url).split('&pageSize=')[0].split('&pageIndex=')[0]+'&pageIndex='+str(int(str(response.url).split('&pageSize=')[0].split('&pageIndex=')[1])+1)+'&pageSize=50&fromDate=&toDate=&displayView=PagingPartial'
            yield Request(tyj) #自增


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] =soup.select_one(' .box-title-detail.entry-title').text
        item['category1'] = 'All'
        item['category2'] = None
        item['body'] =soup.select_one(' .detail-content-body').text
        item['abstract'] =soup.select_one(' .box-des-detail.this-one').text.strip('\n')
        item['pub_time'] = response.meta['pub_time_']
        try:
            item['images'] =[soup.select_one(' .box-detail-thumb.uk-text-center').img.get('src')]
        except:
            item['images'] = []
        yield item # 爬虫虽小，五脏俱全