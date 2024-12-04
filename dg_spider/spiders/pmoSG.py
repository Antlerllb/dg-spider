# encoding: utf-8
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


#Author:陈卓玮
# check: 凌敏 有id错误，已改 pass
class pmoSGSpider(BaseSpider):
    name = 'pmoSG'
    website_id = 456
    language_id = 1866
    start_urls = ['https://www.pmo.gov.sg/Topics']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        for i in soup.select('#block-system-main > div > div'):
            yield Request(url="https://www.pmo.gov.sg" + i.select_one('a').get('href')
                          ,callback=self.parsepages)
    def parsepages(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        for k in soup.select('.topic-item'):
            title = (k.select_one('.gamma').text)#标题
            time = self.format_time(k.select_one('.ti-date').text)#时间
            category=soup.select_one('title').text.split(' | ')[1]#类别
            try:
                essay_url = ("https://www.pmo.gov.sg" + k.select_one('a').get('href'))#页面
                meta = {'title':title,
                        'time':time,
                        'category':category}
                yield Request(url = essay_url,callback=self.parse_essay,meta=meta)
            except:
                pass

        time_stamp = OldDateUtil.str_datetime_to_timestamp(time)
        if(OldDateUtil.time == None or int(time_stamp) >= OldDateUtil.time):
            try:
                yield Request(url = response.url.split('?')[0] + soup.select_one('.next a').get('href')
                              ,callback=self.parsepages)#翻页
            except:
                pass
    def parse_essay(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        meta = response.meta

        body=''
        for i in soup.select('p'):
            body+=i.text + '\n'
        img=[]
        for i in soup.select('img'):
            img.append("https://www.pmo.gov.sg/" + i.get('src'))
        item = NewsItem(language_id=self.language_id)
        item['title'] = meta['title']
        item['category1'] = meta['category']
        item['body'] = body.replace(" ",'')
        item['abstract'] = body.replace(" ",'').split('\n')[0]+body.replace(" ",'').split('\n')[1]
        item['pub_time'] = meta['time']
        item['images'] = img
        # print(item)
        yield item


    def format_time(self,raw):
        raw = raw.split(' ')
        day = raw[0]
        month = str(OldDateUtil.EN_1866_DATE[raw[1]]).zfill(2)
        year = raw[2]
        return year+"-"+month+"-"+day+" 00:00:00"