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
from scrapy.http.request.form import FormRequest
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


# Author:陈卓玮
# check：凌敏 pass

class mier_spider(BaseSpider):
    name = 'mier'
    website_id = 708
    language_id = 2037
    start_urls = ['https://www.mier.org.my/op-ed/page/1']

    def parse(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.select('#pro-gallery-margin-container a div article'):
            time = (i.select_one('div ul li .post-metadata__date').text)
            title = (i.select_one('h2').text)
            url = (i.select_one("div > div.JMCi2v.blog-post-homepage-link-hashtag-hover-color.so9KdE.lyd6fK > a").get(
                'href'))
            abstract = (i.select_one('.BOlnTh').text)
            yield Request(url = url,callback=self.parse_essay,meta={'time':time,'title':title,'abstract':abstract})

        time = (soup.select_one('#pro-gallery-margin-container a div article div ul li .post-metadata__date').text)
        try:
            if OldDateUtil.time==None or OldDateUtil.time <=OldDateUtil.str_datetime_to_timestamp(self.format_time(time)):
                n_url = (soup.find('a', {'aria-label': 'Next page'}).get('href'))
                yield Request(url=n_url)
        except:
            pass

    def parse_essay(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = 'News'
        item['body'] = ''.join([i.text for i in soup.select('article p')])
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = self.format_time(response.meta['time'])
        item['images'] = [i.get('src') for i in soup.select('img')]
        yield item

    def format_time(self,time):
        if 'ago' in time:
            day = int(time.split(' ')[0])
            return OldDateUtil.timestamp_to_datetime_str(OldDateUtil.get_time_ago_stamp(day=day))

        elif len(time.split(' ')) == 2:
            day = time.split(' ')[1]
            month = str(OldDateUtil.EN_1866_DATE[time.split(' ')[0]]).zfill(2)
            year = '2022'
            return year + '-' + month + '-' + day + ' 00:00:00'

        elif len(time.split(' ')) == 3:
            time = time.replace(',', '')
            day = time.split(' ')[1]
            month = str(OldDateUtil.EN_1866_DATE[time.split(' ')[0]]).zfill(2)
            year = time.split(' ')[2]
            return year + '-' + month + '-' + day + ' 00:00:00'

