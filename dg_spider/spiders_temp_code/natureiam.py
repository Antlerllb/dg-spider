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
import requests
import scrapy
from dg_spider.items import NewsItem
import scrapy
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
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
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
class NatureiamSpider(BaseSpider):  # 类名重命名
    author = "张鸿兴"
    name = 'natureiam'  # name的重命名
    language_id = 2122
    website_id = 2188  # id一定要填对！
    start_urls = ['https://nature.iam.gov.mo/c/news/list',
                  'https://nature.iam.gov.mo/p/news/list',
                  'https://nature.iam.gov.mo/e/news/list']
    lan_num = 3

    @staticmethod
    def formalize(category, title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ').replace('\n', '')
        title = re.sub(' +', ' ', title).strip().strip('\n')
        body = re.sub('<br>.*?<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub(' +', ' ', body).strip()
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        if language_id == 1813:
            category, title, abstract, body = convert(category, 'zh-cn'), convert(title, 'zh-cn'), \
                                              convert(abstract, 'zh-cn'), convert(body, 'zh-cn'),
        return category, title, abstract, body

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        url = response.request.url
        if "/p/" in url:
            response.meta['language_id'] = 2122
        elif "/c/" in url:
            response.meta['language_id'] = 1813
        elif "/e/":
            response.meta['language_id'] = 1866
        block_list = soup.select('div.thumbnailDiv.col-sm-6.col-md-4.col-lg-4')
        # print(block_list)
        if len(block_list) == 0:
            block_list = soup.select('div.col-lg-4.col-md-6.col-sm-6.fthumbnaildiv')
        for block in block_list:
            href = url[0:url.find('.mo/') + 3] + block.select_one('a')['href']
            # print(href)
            '#list1Div > div:nth-child(1) > a > div > div.caption'
            time_list = block.select_one('div.caption').text.strip().split('\n')[1].strip().split('/')
            pub_time = f'{time_list[2]}-{time_list[1].zfill(2)}-{time_list[0].zfill(2)} 00:00:00'
            response.meta['pub_time'] = pub_time
            # print(pub_time)
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)

    def parse_items(self, response):
        url = response.request.url
        # print(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        article = soup.select_one('article')
        f = 0
        item['pub_time'] = response.meta['pub_time']
        body_text = re.sub('\n+', '\n', article.text.strip()).split('\n')
        for i in range(0, len(body_text)):
            if '簡介' in body_text[i] or 'Introduction' in body_text[i] or 'Introdução' in body_text[i]:
                f = 1
                body_text = body_text[i + 1:]
                break
        if f == 0:
            for i in range(0, len(body_text)):
                if '日期' in body_text[i] or 'Date' in body_text[i] or 'Dia' in body_text[i]:
                    body_text = body_text[i + 1:]
                    break
        body = re.sub('\n+', '\n', '\n'.join(body_text).strip())
        body = re.sub(' +', ' ', body)
        category_list = soup.select_one('div#navbar').text.strip().split('>')
        item['category1'] = category_list[1].strip()
        title = soup.select_one('div.titleDiv').text.strip()
        title = re.sub(' +', ' ', title)
        images_list = article.select('picture.image-gallery-img')
        images = []
        for i in images_list:
            img = i.select_one('source')['srcset']
            # print(images)
            images.append(img)
        # print(images)
        item['images'] = images
        if "/p/" in url:
            response.meta['language_id'] = 2122
        elif "/c/" in url:
            response.meta['language_id'] = 1813
        elif "/e/":
            response.meta['language_id'] = 1866
        item['language_id'] = response.meta['language_id']
        item['category1'], item['title'], item['abstract'], item['body'] = \
            self.formalize(item['category1'], title, None, body, item['language_id'])
        # print(item)
        if item['body'] is not None and len(item['body']) >= 2:
            yield item
