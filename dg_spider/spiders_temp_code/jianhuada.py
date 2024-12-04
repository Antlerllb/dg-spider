#encoding: utf-8




from scrapy.http.request import Request
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
from scrapy.http import Request, Response
import re
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




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

class JianhuadaSpider(BaseSpider):
    name = 'jianhuada'
    author = '王伟任'
    website_id = 282
    language_id = 2266
    # 将 start_urls 初始化为空列表

    start_urls = ['https://www.jianhuadaily.com/c/khmer-news/page/1',
                 'https://www.jianhuadaily.com/c/khmer-news/page/2',
                 'https://www.jianhuadaily.com/c/khmer-news/page/3',
                 'https://www.jianhuadaily.com/c/khmer-news/page/4',
                 'https://www.jianhuadaily.com/c/khmer-news/page/5',
                 'https://www.jianhuadaily.com/c/khmer-news/page/6',
                 'https://www.jianhuadaily.com/c/khmer-news/page/7',
                 'https://www.jianhuadaily.com/c/khmer-news/page/8',
                 'https://www.jianhuadaily.com/c/khmer-news/page/9',
                 'https://www.jianhuadaily.com/c/khmer-news/page/10',
                 'https://www.jianhuadaily.com/c/khmer-news/page/11',
                 'https://www.jianhuadaily.com/c/khmer-news/page/1',
                  'https://www.jianhuadaily.com/c/khmer-news/page/2',
                  'https://www.jianhuadaily.com/c/khmer-news/page/3',
                  'https://www.jianhuadaily.com/c/khmer-news/page/4',
                  'https://www.jianhuadaily.com/c/khmer-news/page/5',
                  'https://www.jianhuadaily.com/c/khmer-news/page/6',
                  'https://www.jianhuadaily.com/c/khmer-news/page/7',
                  'https://www.jianhuadaily.com/c/khmer-news/page/8',
                  'https://www.jianhuadaily.com/c/khmer-news/page/9',
                  'https://www.jianhuadaily.com/c/khmer-news/page/10',
                  'https://www.jianhuadaily.com/c/khmer-news/page/11',
                  'https://www.jianhuadaily.com/c/khmer-news/page/1',
                  'https://www.jianhuadaily.com/c/khmer-news/page/2',
                  'https://www.jianhuadaily.com/c/khmer-news/page/3',
                  'https://www.jianhuadaily.com/c/khmer-news/page/4',
                  'https://www.jianhuadaily.com/c/khmer-news/page/5',
                  'https://www.jianhuadaily.com/c/khmer-news/page/6',
                  'https://www.jianhuadaily.com/c/khmer-news/page/7',
                  'https://www.jianhuadaily.com/c/khmer-news/page/8',
                  'https://www.jianhuadaily.com/c/khmer-news/page/9',
                  'https://www.jianhuadaily.com/c/khmer-news/page/10',
                  'https://www.jianhuadaily.com/c/khmer-news/page/11'
                  'https://www.jianhuadaily.com/c/khmer-news/page/1','https://www.jianhuadaily.com/c/khmer-news/page/2','https://www.jianhuadaily.com/c/khmer-news/page/3','https://www.jianhuadaily.com/c/khmer-news/page/4','https://www.jianhuadaily.com/c/khmer-news/page/5','https://www.jianhuadaily.com/c/khmer-news/page/6','https://www.jianhuadaily.com/c/khmer-news/page/7','https://www.jianhuadaily.com/c/khmer-news/page/8','https://www.jianhuadaily.com/c/khmer-news/page/9','https://www.jianhuadaily.com/c/khmer-news/page/10','https://www.jianhuadaily.com/c/khmer-news/page/11'
                  'https://www.jianhuadaily.com/c/khmer-news/page/1','https://www.jianhuadaily.com/c/khmer-news/page/2','https://www.jianhuadaily.com/c/khmer-news/page/3','https://www.jianhuadaily.com/c/khmer-news/page/4','https://www.jianhuadaily.com/c/khmer-news/page/5','https://www.jianhuadaily.com/c/khmer-news/page/6','https://www.jianhuadaily.com/c/khmer-news/page/7','https://www.jianhuadaily.com/c/khmer-news/page/8','https://www.jianhuadaily.com/c/khmer-news/page/9','https://www.jianhuadaily.com/c/khmer-news/page/10','https://www.jianhuadaily.com/c/khmer-news/page/11'
                  'https://www.jianhuadaily.com/c/khmer-news/page/1','https://www.jianhuadaily.com/c/khmer-news/page/2','https://www.jianhuadaily.com/c/khmer-news/page/3','https://www.jianhuadaily.com/c/khmer-news/page/4','https://www.jianhuadaily.com/c/khmer-news/page/5','https://www.jianhuadaily.com/c/khmer-news/page/6','https://www.jianhuadaily.com/c/khmer-news/page/7','https://www.jianhuadaily.com/c/khmer-news/page/8','https://www.jianhuadaily.com/c/khmer-news/page/9','https://www.jianhuadaily.com/c/khmer-news/page/10','https://www.jianhuadaily.com/c/khmer-news/page/11'
                  'https://www.jianhuadaily.com/c/khmer-news/page/1','https://www.jianhuadaily.com/c/khmer-news/page/2','https://www.jianhuadaily.com/c/khmer-news/page/3','https://www.jianhuadaily.com/c/khmer-news/page/4','https://www.jianhuadaily.com/c/khmer-news/page/5','https://www.jianhuadaily.com/c/khmer-news/page/6','https://www.jianhuadaily.com/c/khmer-news/page/7','https://www.jianhuadaily.com/c/khmer-news/page/8','https://www.jianhuadaily.com/c/khmer-news/page/9','https://www.jianhuadaily.com/c/khmer-news/page/10','https://www.jianhuadaily.com/c/khmer-news/page/11'
                  'https://www.jianhuadaily.com/c/khmer-news/page/2',
                  'https://www.jianhuadaily.com/c/khmer-news/page/3',
                  'https://www.jianhuadaily.com/c/khmer-news/page/4',
                  'https://www.jianhuadaily.com/c/khmer-news/page/5',
                  'https://www.jianhuadaily.com/c/khmer-news/page/6',
                  'https://www.jianhuadaily.com/c/khmer-news/page/7',
                  'https://www.jianhuadaily.com/c/khmer-news/page/8',
                  'https://www.jianhuadaily.com/c/khmer-news/page/9',
                  'https://www.jianhuadaily.com/c/khmer-news/page/10',
                  'https://www.jianhuadaily.com/c/khmer-news/page/11'

                  ]


    def parse(self, response):

        url_list = response.xpath('//*[@id="content"]/div/div/div[1]/div[1]/article/div/h2/a/@href').extract()
        for class_url in url_list:
            time_pre = class_url
            date_str = time_pre.split('/')[3]  # 提取出 '20240928'
            year = date_str[:4]
            month = date_str[4:6]
            day = date_str[6:8]
            pub_time = f"{year}-{month}-{day} 00:00:00"
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            images =[]

            response.meta['images'] = images
            response.meta['pub_time'] = pub_time
            yield scrapy.Request(class_url, callback=self.parse_item, meta=response.meta)

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        category1 = 'ភាសាខ្មែរ'
        title = response.xpath('//div[@class="entry-content clearfix single-post-content"]/../../article/div/h1/span/text()').extract()
        body = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p/text()').extract()
        if not body:
            body = ['ភាសាខ្មែរ']
        else:
            body = [re.sub(r'[\u00a0\u200b]+', '', text) for text in body]



        abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p/text()').extract_first()

        if abstract == '&nbsp;':
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[2]/text()').extract_first()
        if abstract == None:
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[2]/text()').extract_first()
        if abstract == []:
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[2]/text()').extract_first()
        if abstract == '':
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[2]/text()').extract_first()

        if abstract == '&nbsp;':
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[3]/text()').extract_first()
        if abstract == None:
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[3]/text()').extract_first()
        if abstract == []:
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[3]/text()').extract_first()
        if abstract == '':
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[3]/text()').extract_first()


        if abstract == '&nbsp;':
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[4]/text()').extract_first()
        if abstract == None:
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[4]/text()').extract_first()
        if abstract == []:
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[4]/text()').extract_first()
        if abstract == '':
            abstract = response.xpath('//div[@class="entry-content clearfix single-post-content"]/p[4]/text()').extract_first()



        if abstract == '&nbsp;':
            abstract = 'ភាសាខ្មែរ'
        if abstract == None:
            abstract = 'ភាសាខ្មែរ'
        if abstract == []:
            abstract = 'ភាសាខ្មែរ'
        if abstract == '':
            abstract = 'ភាសាខ្មែរ'
        if len(abstract) <=2:
            abstract = 'ភាសាខ្មែរ'

        if not abstract:
            abstract = 'ភាសាខ្មែរ'
        else:
            abstract = re.sub(r'[\u00a0\u200b]+', '', abstract)
        # print(abstract)
        body = '\n'.join(body)
        if '\n' not in body:
            body = abstract + '\n' + body


        language_id = 1982
        item['language_id'] = language_id
        item['body'] = body
        item['title'] = title
        item['abstract'] = abstract
        item['images'] = response.meta['images']
        item['category1'] = category1
        item['pub_time'] = response.meta['pub_time']

        yield item


