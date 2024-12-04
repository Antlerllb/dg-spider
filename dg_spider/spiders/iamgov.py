# encoding: utf-8
import datetime
import html
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
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
class IamgovSpider(BaseSpider):  # 类名重命名
    author = "张鸿兴"
    name = 'iamgov'  # name的重命名
    language_id = 2122
    website_id = 2159  # id一定要填对！
    start_urls = ['https://www.iam.gov.mo/s/news/list', 'https://www.iam.gov.mo/p/news/list',
                  'https://www.iam.gov.mo/e/news/list']

    # start_urls = ['http://www.iam.gov.mo/s/news/list']

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
        body = re.sub('<br>　　<br>', '\n', body)
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
        abstract = re.sub('<[^>]+>', '', abstract)
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        return title, abstract, body

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        url = response.request.url
        if "/p/" in url:
            response.meta['language_id'] = 2122
            response.meta['category1'] = 'Notícias'
        elif "/s/" in url:
            response.meta['language_id'] = 1813
            response.meta['category1'] = '新闻'
        elif "/e/":
            response.meta['language_id'] = 1866
            response.meta['category1'] = 'News'
        block = soup.select_one('#list > div').select('a')
        for i in block:
            time_list = i.parent.next_sibling.text.split('/')
            pub_time = f'{time_list[2]}-{time_list[1]}-{time_list[0]} 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            response.meta['pub_time'] = pub_time
            response.meta['title'] = i.text
            href = 'https://www.iam.gov.mo' + i['href']
            yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)

    def parse_items(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        body_list = soup.select('p')
        body = ""
        for i in body_list:
            body += i.text
            body += '\n'
        item = NewsItem(language_id=self.language_id)
        item['language_id'] = response.meta['language_id']
        item['title'], item['abstract'], item['body'] = self.formalize(response.meta['title'],
                                                                       body.strip().split('\n')[0],
                                                                       body, item['language_id'])
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        images_list = soup.select('#photos > a')
        images = []
        for i in images_list:
            images.append('https://www.iam.gov.mo' + i['href'])
        item['images'] = images

        yield item
