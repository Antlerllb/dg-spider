# -*- coding: utf-8 -*-
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
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil




from scrapy.http.request import Request
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
from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class OrldnotecomSpider(BaseSpider):
    author = '王伟任'
    name = 'orldnotecom'
    website_id = 2240
    language_id = 1963
    start_urls = ['https://world-note.com/category/world-people/']
    lan_num = 1

    @staticmethod
    def cut_noneed_str(pre_str):
        pre_str = pre_str.replace("\u200b", "")
        pre_str = pre_str.replace("\u3000", "")
        pre_str = pre_str.replace("\xa0", "")
        pre_str = pre_str.replace("\u202f", "")
        pre_str = pre_str.replace("\t", "")
        pre_str = pre_str.replace("\r", "")
        return pre_str

    def parse(self, response):
        category1 = response.xpath('//h1 [@class="archive-title"]/text()').extract_first()
        response.meta['category1'] = category1
        for num in range(0, 18):
            time = response.xpath(
                '//div[@class="entry-card-content card-content e-card-content"]/div/div/span [@class="post-date"]/text()').extract()[
                num]
            time = time.replace('.', '-')
            pub_time = time + ' 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return

            title = response.xpath('//div [@class="entry-card-content card-content e-card-content"]/h2/text()').extract()[num]
            title = ''.join(title)
            title = self.cut_noneed_str(title)

            abstract = response.xpath('//div [@class="entry-card-content card-content e-card-content"]/div/text()').extract()[num]
            abstract = ''.join(abstract)
            abstract = self.cut_noneed_str(abstract)

            images = response.xpath(
                '//div [@class="entry-card-content card-content e-card-content"]/../figure/img/@src').extract()[num]
            images = [images]

            web_href = response.xpath('//div [@class="entry-card-content card-content e-card-content"]/../../@href').extract()[num]

            response.meta['pub_time'] = pub_time
            response.meta['web_href'] = web_href
            response.meta['title'] = title
            response.meta['abstract'] = abstract
            response.meta['images'] = images

            yield scrapy.Request(web_href, callback=self.parse_item, meta=response.meta)

        for page_num in range(2, 32):
            next_url = f'https://world-note.com/category/world-people/page/{page_num}/'
            category1 = '世界の人々'
            response.meta['category1'] = category1
            yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

        for page_num in range(1, 8):
            next_url = f'https://world-note.com/category/world-civilization-culture/page/{page_num}/'
            category1 = '世界の文明・文化'
            response.meta['category1'] = category1
            yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

        for page_num in range(1, 4):
            next_url = f'https://world-note.com/category/religions/page/{page_num}/'
            category1 = '世界の宗教'
            response.meta['category1'] = category1
            yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

        for page_num in range(1, 79):
            next_url = f'https://world-note.com/page/{page_num}/'
            category1 = '世界のあれこれ'
            response.meta['category1'] = category1
            yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

        for page_num in range(1, 50):
            next_url = f'https://world-note.com/category/various-countries/page/{page_num}/'
            category1 = '世界各国の情報'
            response.meta['category1'] = category1
            yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)




    def parse_item(self, response):

        item = NewsItem(language_id=self.language_id)
        pub_time = response.meta['pub_time']
        title = response.meta['title']
        abstract = response.meta['abstract']
        images = response.meta['images']
        category1 = response.meta['category1']
        if category1 == None:
            category1 = '世界各国の情報'

        body = response.xpath('//div[@ class="entry-content cf"] /p/text()').extract()
        body = '\n'.join(body)
        body = self.cut_noneed_str(body)
        if "\n" not in body:
            body = abstract + "\n" + body
        if body == "\n":
            body = abstract + "\n" + "N"


        item['pub_time'] = pub_time
        item['title'] = title
        item['abstract'] = abstract
        item['images'] = images
        item['category1'] = category1
        item['body'] = body

        yield item


