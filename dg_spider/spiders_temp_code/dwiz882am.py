import socket

import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


# 此文件包含的头文件不要修改
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

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http import Request, Response
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http import FormRequest

from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re
import scrapy
import requests

global null
null = ''


# author:魏芃枫


class Dwiz882am(BaseSpider):
    name = 'dwiz882am'
    start_urls = ['https://www.dwiz882am.com/']
    website_id = 1914  # 网站的id(必填)
    language_id = 1880  # 所用语言的id
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        category1_list = soup.select('.theiaStickySidebar .inner-arrow a')
        for i in category1_list:
            category1 = i.text
            meta1 = {'category1': category1}
            category1_href = i.get('href')
            yield Request(category1_href, callback=self.parse_pages, meta=meta1)

    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        title_list = soup.select('h2 a')
        for i in title_list:
            e_time = soup.select_one('.penci-box-meta span').text
            year = e_time.split(',')[1].strip()
            month_day = e_time.split(',')[0]
            month = month_day.split(' ')[0]
            day = month_day.split(' ')[1]
            pub_time = year + '-' + str(OldDateUtil.EN_1866_DATE[month]).zfill(2) + '-' + day + ' 00:00:00'
            timestamp = OldDateUtil.str_datetime_to_timestamp(pub_time)
            try:
                if OldDateUtil.time == None or timestamp >= int(OldDateUtil.time):
                    href = i.get('href')
                    meta2 = {'pub_time': pub_time}
                    meta2.update(response.meta)
                    yield Request(href, callback=self.parse_article, meta=meta2)
                else:
                    self.logger.info('时间截止！')
            except:
                continue
        # 查找下一页URL 该网站只能通过点击下一页而不能点击页数
        try:
            nextpage_url = soup.select_one(".older a").get('href')
            yield Request(nextpage_url, callback=self.parse_pages,meta=response.meta)
        except:
            self.logger.info("No more pages")



    def parse_article(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        image_flag = 1
        try:
            src = soup.select_one('.post-image a img').get('src')
        except:
            image_flag = 0

        title = soup.select_one('h1').text
        paragraphs = soup.select('.post-entry p')
        abstract = paragraphs[0].text
        body = ''
        for i in paragraphs[0:-1]:
            body += i.text

        item = NewsItem(language_id=self.language_id)
        item['title'] = title
        item['pub_time'] = response.meta['pub_time']
        item['body'] = body
        item['abstract'] = abstract
        item['category1'] = response.meta['category1']
        item['category2'] = None
        if image_flag == 1:
            item['images'] = src
        else:
            item['images'] = None
        return item
