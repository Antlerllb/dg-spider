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
# check: 凌敏 pass
#debug: 增加翻页限制

class UnitedSpider(BaseSpider):
    name = 'UD_news'
    website_id = 178
    language_id = 2266
    start_urls = ['https://weareunited.com.my/author/wkyong/page/1']

    def parse(self, response):#获取新闻列表
        soup=BeautifulSoup(response.text,'lxml')
        for i in soup.select('#content > div > div.row.gridlove-posts > div'):
            time_stamp = self.time_parser(i.select_one('.updated').text)
            title = i.select_one('h2').text
            essay_url= i.select_one('h2 a').get('href')
            abstract = i.select_one('.entry-content').text
            meta={'time':time_stamp,'title':title,'abstract':abstract}
            # print(OldDateUtil.time_stamp2formate_time(time_stamp))
            yield Request(url = essay_url,callback=self.parse_essay,meta=meta)

        time_stamp = self.time_parser(soup.select_one('#content > div > div.row.gridlove-posts > div .updated').text)##翻页
        if (time_stamp!=None) and (OldDateUtil.time == None or time_stamp >= OldDateUtil.time):
            if "page" not in response.url:
                # print('next_url=>',response.url+"page/2")
                yield Request(url=response.url+"page/2")
            elif int(response.url.split('/page/')[1].strip('/'))< 3708:
                # print('next_url=>',response.url.split('/page/')[0]+"/page/"+str(int(response.url.split('/page/')[1].strip('/'))+1))
                yield Request(url = response.url.split('/page/')[0]+"/page/"+str(int(response.url.split('/page/')[1].strip('/'))+1))

    def parse_essay(self,response):
        soup = BeautifulSoup(response.text,'lxml')

        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = soup.select_one(".entry-category").text
        item['body'] = soup.select_one('.entry-content').text
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = OldDateUtil.timestamp_to_datetime_str(response.meta['time'])
        img=[]
        for i in soup.select('img'):
            img.append(i.get('src'))
        item['images'] = img
        # print(item)
        yield item


    def time_parser(self,raw):
        if raw == None:
            return None

        elif 'ago' in raw:
            stamp = OldDateUtil.str_datetime_to_timestamp(OldDateUtil.get_now_datetime_str())
            return stamp

        else:
            raw = raw.split(' ')
            raw = raw[2] +"-" + str(OldDateUtil.EN_1866_DATE[raw[1].strip(',')]).zfill(2) + "-" + raw[0] + " 00:00:00"
            stamp = OldDateUtil.str_datetime_to_timestamp(raw)
            return stamp
