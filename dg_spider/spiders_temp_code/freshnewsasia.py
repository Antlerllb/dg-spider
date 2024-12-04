import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy


import random



class FreshnewsasiaSpider(BaseSpider):
    name = 'freshnewsasia'
    website_id = 2694
    language_id = 2275
    author = '马波生'
    start_urls = ['https://www.freshnewsasia.com']

    def parse(self, response):
        category1 = response.xpath('/html/body/div[3]/div/header/div/div[2]/div/p/a/text()').extract()
        for i in range(0, 500, 50):
            links = f'http://www.freshnewsasia.com/index.php/en/?start={i}'
            yield scrapy.Request(url=links, callback=self.parse_page,
                                 meta={'category1': category1})

    def parse_page(self, response):
        page_links = response.xpath('//*[@id="adminForm"]/table/tbody/tr/td/a/@href').extract()
        for link in page_links:
            real_link = 'http://www.freshnewsasia.com' + link
            yield scrapy.Request(url=real_link, callback=self.parse_detail,
                                 meta=response.meta)

    def parse_detail(self, response):
        item = NewsItem(language_id=self.language_id)
        pub_time = response.xpath('//*[@id="content"]/div[3]/dl/dd/time/text()').extract()
        pub_time = [a.strip() for a in pub_time][0]
        pub_time = pub_time[:-2]
        pub_time = pub_time + ':00'
        if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
            return
        title = response.xpath('//*[@id="content"]/div[3]/div[1]/h2/text()').extract()
        title = [a.strip() for a in title][0]
        abstracts = response.xpath('//*[@id="content"]/div[3]/div[2]/p[1]/text()').extract()
        abstract = [a.strip() for a in abstracts][0]
        body = ''
        bodys = response.xpath('//*[@id="content"]/div[3]/div[2]/p/text()').extract()
        for b in bodys:
            body += b.strip() + '\n\n'
        image = response.xpath('//*[@id="content"]/div[3]/div[2]/p/img/@src').extract()
        category1 = response.meta['category1']
        category = ''
        for c in category1:
            category += c
        item['title'] = title
        item['abstract'] = abstract
        item['body'] = body
        item['category1'] = category
        item['images'] = image
        item['pub_time'] = pub_time
        # print(item)
        yield item









