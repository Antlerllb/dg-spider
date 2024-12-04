#-*- coding: utf-8 -*-
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


class JapantodaySpider(BaseSpider):
    author = '王伟任'
    name = 'japantoday'
    website_id = 1982
    language_id = 1866
    start_urls = ['https://japantoday.com/category/national?page=1',
                  'https://japantoday.com/category/entertainment?page=1',
                  'https://japantoday.com/category/politics?page=1', 'https://japantoday.com/category/business?page=1',
                  'https://japantoday.com/category/crime?page=1', 'https://japantoday.com/category/tech?page=1',
                  'https://japantoday.com/category/sports?page=1', 'https://japantoday.com/category/world?page=1']
    lan_num = 1

    def parse(self, response):

        for num in range(0, 9):
            time = response.xpath('//div [@class="media media-sm"]/div/div/time[1]/@datetime').extract()[num]
            pub_time = time[0] + time[1] + time[2] + time[3] + time[4] + time[5] + time[6] + time[7] + time[8] + time[
                9] + " " + time[11] + time[12] + time[13] + time[14] + time[15] + time[16] + time[17] + time[18]
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            title = response.xpath('//div [@class="media media-sm"]/div/h3/a/text()').extract()[num]
            title = ''.join(title)
            title = title.replace("\u200b", "")
            title = title.replace("\u3000", "")
            title = title.replace("\xa0", "")
            title = title.replace("\u202f", "")

            pre_website_href = response.xpath('//div [@class="media media-sm"]/div/h3/a/@href').extract()[num]
            website_href = "https://japantoday.com" + pre_website_href
            abstract = response.xpath('//div [@class="media media-sm"]/div/p/text()').extract()[num]
            abstract = "".join(abstract)
            abstract = abstract.replace("\u200b", "")
            abstract = abstract.replace("\u202f", "")
            abstract = abstract.replace("\u3000", "")
            abstract = abstract.replace("\xa0", "")

            response.meta['pub_time'] = pub_time
            response.meta['website_href'] = website_href
            response.meta['title'] = title
            response.meta['abstract'] = abstract

            yield scrapy.Request(website_href, callback=self.parse_item, meta=response.meta)
            if "national" in website_href:
                for page_num in range(2, 86):
                    next_url = f'https://japantoday.com/category/national?page={page_num}'
                    response.meta['next_url'] = next_url
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            if "business" in website_href:
                for page_num in range(3, 81):
                    next_url = f'https://japantoday.com/category/business?page={page_num}'
                    response.meta['next_url'] = next_url
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            if "entertainment" in website_href:
                for page_num in range(2, 81):
                    next_url = f'https://japantoday.com/category/entertainment?page={page_num}'
                    response.meta['next_url'] = next_url
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            if "politics" in website_href:
                for page_num in range(2, 81):
                    next_url = f'https://japantoday.com/category/politics?page={page_num}'
                    response.meta['next_url'] = next_url
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            if "crime" in website_href:
                for page_num in range(2, 81):
                    next_url = f'https://japantoday.com/category/crime?page={page_num}'
                    response.meta['next_url'] = next_url
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            if "tech" in website_href:
                for page_num in range(2, 81):
                    next_url = f'https://japantoday.com/category/tech?page={page_num}'
                    response.meta['next_url'] = next_url
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            if "sports" in website_href:
                for page_num in range(2, 81):
                    next_url = f'https://japantoday.com/category/sports?page={page_num}'
                    response.meta['next_url'] = next_url
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            if "world" in website_href:
                for page_num in range(2, 81):
                    next_url = f'https://japantoday.com/category/world?page={page_num}'
                    response.meta['next_url'] = next_url
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

    def parse_item(self, response):

        item = NewsItem(language_id=self.language_id)
        next_url = response.meta['next_url']
        pub_time = response.meta['pub_time']
        title = response.meta['title']
        abstract = response.meta['abstract']
        if "national" in next_url:
            category1 = "NATIONAL"
            response.meta['category1'] = category1
        if "business" in next_url:
            category1 = "BUSINESS"
            response.meta['category1'] = category1
        if "entertainment" in next_url:
            category1 = "ENTERTAINMENT"
            response.meta['category1'] = category1
        if "politics" in next_url:
            category1 = "POLITICS"
            response.meta['category1'] = category1

        if "crime" in next_url:
            category1 = "CRIME"
            response.meta['category1'] = category1
        if "tech" in next_url:
            category1 = "TECH"
            response.meta['category1'] = category1
        if "sports" in next_url:
            category1 = "SPORTS"
            response.meta['category1'] = category1
        if "world" in next_url:
            category1 = "WORLD"
            response.meta['category1'] = category1
        images = response.xpath('//div [@class="row gutter-sm"]/article/figure/img/@src').extract()
        body_list = response.xpath('//div[@ itemprop="articleBody"]/p/text()').extract()
        body = '\n'.join(body_list)
        body = body.replace("\u200b", "")
        body = body.replace("\u3000", "")
        body = body.replace("\u202f", "")
        body = body.replace("\xa0", "")
        if "\n" not in body_list:
            body = abstract + "\n" + body
        if body == "\n":
            body = abstract + "\n" + "N"
        item['body'] = body
        item['title'] = title
        item['abstract'] = abstract
        item['images'] = images
        item['category1'] = category1
        item['pub_time'] = pub_time

        yield item
