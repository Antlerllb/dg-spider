# -*- coding = utf-8 -*-
# @Time : 5:21 下午
# @Author : 阿童木
# @File : haberler.py
# @software: PyCharm



from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil as mutong
import re
from scrapy import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil




#author:李沐潼

class haberlerSpider(BaseSpider):
    name = 'haberler'
    website_id = 1814
    language_id = 2227
    start_urls = ['https://www.haberler.com/magazin/']

    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta = {'category1': 'Magazin Haberleri'}
        category=soup.select('.hbftcolContent>.hbftCol>a')
        for item in category:
            meta['category2']=item.get('title')
            yield Request(item.get('href'),meta=meta,callback=self.parse_news)

    def parse_news(self, response):
        soup = mutong(response.text, 'html.parser')
        news=soup.select('.p12-col>a')
        for item in news:
            url='https://www.haberler.com'+item.get('href')
            yield Request(url, meta=response.meta, callback=self.parse_items)
    def parse_items(self,response):
        soup=mutong(response.text,'html.parser')
        t_a=soup.select('time')
        #print(t_a)
        if t_a!=[]:
            t = t_a[0].get('datetime')
            tt = t.split('T')
            t_formal = tt[0] + ' ' + tt[1][:8]
         #   print(t_formal)

            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(t_formal) >= int(OldDateUtil.time):
                item = NewsItem(language_id=self.language_id)
                item['title'] = soup.select('header>h1')

                item['category1'] = response.meta['category1']
                item['category2'] = response.meta['category2']
                item['body'] = ' '.join([i.text for i in soup.select('main>p')])
                item['abstract'] = soup.select('header>h2')
                item['pub_time'] = t_formal
                if soup.select('img') !=[]:
                    item['images'] =soup.select('img')[0].get('data-src')
                else:
                    item['images']=None
                    #print(soup.select('img'))
                yield item
            else:
                return

