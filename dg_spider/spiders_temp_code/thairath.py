# encoding: utf-8
import json

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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil as t


#Author:陈卓玮
# check：凌敏 pass
class thairahSpider(BaseSpider):
    name = 'thairah'
    website_id = 1567
    language_id = 2208
    ts_now = OldDateUtil.str_datetime_to_timestamp(OldDateUtil.get_now_datetime_str()) #获取现在时间
    list_limit = 100
    start_urls = [f'https://www.thairath.co.th/loadmore&ts={ts_now}&limit={list_limit}']###api

    def parse(self, response):
        list_data = json.loads(response.text)
        list_items = list_data['items']
        l_ts = OldDateUtil.str_datetime_to_timestamp(list_items[-1]['publishTime'].split("T")[0] + " " + list_items[-1]['publishTime'].split("T")[1].split("+")[0])
        for i in list_items:
            url = i['canonical']
            time = i['publishTime'].split("T")[0]+" "+i['publishTime'].split("T")[1].split("+")[0]
            abstract = i['abstract']
            category1 = i['section']
            category2 = i['topic']
            title = i['title']
            img=[]
            img.append(i['image'])
            yield Request(url = url,callback=self.essay_parser,meta={'time':time,
                                                                    'abstract':abstract,
                                                                    'category1':category1,
                                                                    'category2':category2,
                                                                    'title':title,
                                                                    'img':img})
        if (OldDateUtil.time == None or l_ts >= OldDateUtil.time) and len(list_items) > 0:
            api = f'https://www.thairath.co.th/loadmore&ts={l_ts}&limit={self.list_limit}'
            t.sleep(10)
            # print(f"正请求{OldDateUtil.time_stamp2formate_time(l_ts)}前的新闻列表！")
            yield Request(api)

    def essay_parser(self,response):
        soup = BeautifulSoup(response.text,'lxml')

        body=''
        for i in soup.select('p'):
            body+=i.text+'\n'

        img = response.meta['img']
        for i in soup.select('img'):
            if 'http' in i.get('src'):
               img.append(i.get('src'))

        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = body
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['time']
        item['images'] = response.meta['img']
        yield item




