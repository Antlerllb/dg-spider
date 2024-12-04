# encoding: utf-8
import html
import json

from bs4 import BeautifulSoup
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
from dg_spider.utils.old_utils import OldDateUtil

# Author:陈卓玮
# check: 凌敏 pass
class govsg_spider(BaseSpider):
    name = 'govsg'
    website_id = 199
    language_id = 1866
    start_urls = ['https://www.gov.sg/']

    def format_time(self,time):
        time = time.split(' ')
        time[0], time[2] = time[2], time[0]
        time[1] = str(OldDateUtil.EN_1866_DATE[time[1]]).zfill(2)
        return ('-'.join(time)+" 00:00:00")

    def parse(self, response):
        category=['Factually','Explainers','Stories','Interviews']

        for cate_name in category:
            params = f"fq=contenttype_s:{cate_name}&" \
                     "sort=publish_date_tdt desc&" \
                     "start=1&rows=50"

            api = 'https://www.gov.sg/api/v1/search'
            meta={'start':1,'rows':50,'cate_name':cate_name}
            time.sleep(5)
            yield Request(url = api+"?"+params,callback=self.parse_essay,meta=meta)

    def parse_essay(self,response):
        cate_name = response.meta['cate_name']
        start=response.meta['start']
        rows=response.meta['rows']
        item = NewsItem(language_id=self.language_id)
        data = json.loads(response.text)
        if len(data['response']['docs'])!=0:
            try:
                time_stamp=OldDateUtil.str_datetime_to_timestamp(self.format_time(data['response']['docs'][-1]['publishdate_s']))
            except:
                time_stamp=OldDateUtil.str_datetime_to_timestamp('2010-01-01 00:00:00')##当翻到最后一页时 文章没有时间

            for i in data['response']['docs']:
                try:
                    item['category2'] = i['primarytopic_s']
                except:
                    pass

                try:
                    item['abstract'] = i['short_description_t']
                except:
                    item['abstract'] = html.escape(i['bodytext_t'].split('\n')[0])
                item['images'] = []
                item['images'].append(i['imageurl_s'])
                item['body'] = i['bodytext_t']
                item['pub_time'] = self.format_time(i['publishdate_s'])
                item['title'] = html.escape(i['title_t'])
                item['category1'] = i['contenttype_s']
                try:
                    t_stamp = OldDateUtil.str_datetime_to_timestamp(self.format_time(i['publishdate_s']))
                except:
                    t_stamp = OldDateUtil.str_datetime_to_timestamp('2010-01-01 00:00:00')

                if OldDateUtil.time == None or t_stamp >= OldDateUtil.time:
                    yield item

            if OldDateUtil.time == None or time_stamp >= OldDateUtil.time :
                start = start+rows
                params = f"fq=contenttype_s:{cate_name}&" \
                         "sort=publish_date_tdt desc&" \
                         f"start={start}&rows={rows}"
                meta={'start':start,'rows':rows,'cate_name':cate_name}
                api = 'https://www.gov.sg/api/v1/search'
                time.sleep(5)
                yield Request(url = api+"?"+params,callback=self.parse_essay,meta=meta)

