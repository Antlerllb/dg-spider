# encoding: utf-8
import datetime
import html
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

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
from scrapy.utils import spider




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
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re


# author : 张鸿兴
class MacaotourismSpider(BaseSpider):  # 类名重命名
    author = "张鸿兴"
    name = 'macaotourism'  # name的重命名
    language_id = 2122
    website_id = 2154  # id一定要填对！
    year = int(OldDateUtil.get_now_datetime_str().split('-')[0])
    month = int(OldDateUtil.get_now_datetime_str().split('-')[1])
    latest_time = "{:0>4d}{:0>2d}".format(year, month)
    start_urls = [
        'https://www.macaotourism.gov.mo/api/enf/whatson?lang=zh-hans&type=&keyword=&m=' + latest_time + '&lang=zh-hans',
        # 'https://www.macaotourism.gov.mo/api/enf/whatson?lang=pt&type=&keyword=&m=' + latest_time + '&lang=pt', 葡语质量差
        'https://www.macaotourism.gov.mo/api/enf/whatson?lang=en&type=&keyword=&m=' + latest_time + '&lang=en']

    @staticmethod
    def formalize(title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ')
        title = title.replace('\t', ' ')
        title = title.replace('\u3000', ' ')
        title = title.replace(' ', ' ')
        title = title.replace('\n', '')
        title = re.sub(' +', ' ', title)
        title = title.strip().strip('\n')
        body = re.sub('<br>.*?<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', ' ')
        body = body.replace('\t', ' ')
        body = body.replace('\u3000', ' ')
        body = body.replace(' ', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub(' +', ' ', body)
        body = body.strip()
        if language_id == 1813:
            body = convert(body, 'zh-cn')
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        return title, abstract, body

    def parse(self, response):
        url = response.request.url
        yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)

    def parse_pages(self, response):
        res = response.json()
        url = response.request.url
        block = res.get('results')
        # 因为有的新闻没有日期只有月份，所以这里将所有无月份的都设置为当月第一天
        for i in block:
            pub_time = i.get('eventDate')
            pub_time = pub_time[0:pub_time.find('~')]
            if len(pub_time) <= 1:
                pub_time = str(self.year) + '-' + str(self.month) + '-01'
            time_list = pub_time.split('-')
            pub_time = f'{time_list[0]}-{time_list[1].zfill(2)}-{time_list[2].zfill(2)} 00:00:00'
            response.meta['pub_time'] = pub_time
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                pass
            item = NewsItem(language_id=self.language_id)
            item['pub_time'] = response.meta['pub_time']
            body = html.unescape(i.get('shortDesc'))
            # print(item['body'])
            abstract = body.strip().split('.' or '。')[0]
            item['category1'] = i.get('types')[0].get('name')
            title = i.get('name')
            if i.get('thumbnail') is not None:
                images = ['https://whatson.macaotourism.gov.mo/' + i.get('thumbnail')]
                item['images'] = images
            url = response.request.url
            # print(url)
            if "lang=pt" in url:
                item['language_id'] = 2122
            elif "lang=zh-hans" in url:
                item['language_id'] = 1813
            elif "lang=en":
                item['language_id'] = 1866
            # print(item)
            item['title'], item['abstract'], item['body'] = self.formalize(title, abstract, body, item['language_id'])
            if item['body'] is not None and len(item['body']) >= 3:
                yield item
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.latest_time = "{:0>4d}{:0>2d}".format(self.year, self.month)
        url = url[0:url.find('&keyword=&m=') + 12] + self.latest_time + url[-1:url.find('&')]
        yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)
