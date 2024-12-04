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

class PortugueseSpider(BaseSpider):
    author = '王伟任'
    name = 'portuguese'
    website_id = 2151
    language_id = 2122
    start_urls = ['https://portuguese.cri.cn/news/comentarios/index.shtml']
    lan_num = 1


    def parse(self, response):
        website_hrefs = response.xpath('//*[@id="ELMTRvUsoXQXOrEEYjqIJuyM230717"]/div/div[2]/h2/a/@href').extract()
        for hrefs_list in website_hrefs:
            class_url = hrefs_list
            response.meta['class_url'] = class_url
            yield scrapy.Request(class_url, callback=self.parse_item, meta=response.meta)


    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)

        pub_time_list = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[2]/span[2]/text()').extract_first()
        if pub_time_list != None:
            pub_time_list = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[2]/span[2]/text()').extract_first().split(' ')
        else:
            pub_time_list = response.xpath('/html/body/div[3]/div[1]/div[1]/span[2]/text()').extract_first()
            if pub_time_list != None:
                pub_time_list = response.xpath('/html/body/div[3]/div[1]/div[1]/span[2]/text()').extract_first().split(' ')
            else:
                pub_time_list = response.xpath('/html/body/div[3]/div[1]/div[1]/span/text()').extract_first().split(' ')
        pub_time = pub_time_list[1] + ' ' + pub_time_list[2]
        # print(pub_time)
        if OldDateUtil.time is not None and  OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
            return


        title = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[1]/text()').extract_first()
        if title == None:
            title = response.xpath('/html/body/div[3]/div[1]/h1/text()').extract_first()

        body_list = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[3]/p/text()').extract()
        if body_list == None:
                body_list = response.xpath('/html/body/div[3]/div[1]/div[2]/p/text()').extract()
        if body_list == []:
            body_list = response.xpath('/html/body/div[3]/div[1]/div[2]/p/text()').extract()
            if body_list == '':
                body_list = response.xpath('/html/body/div[3]/div[1]/div[2]/p/text()').extract()

        body = '\n'.join(body_list)

        abstract = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[3]/p[2]/text()').extract_first()
        if abstract == None:
            abstract = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[3]/p[3]/text()').extract_first()
            if abstract == None:
                abstract = response.xpath('/html/body/div[3]/div[1]/div[2]/p[1]/text()').extract_first()
                if abstract == None:
                    abstract = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[3]/p[3]/text()').extract_first()
                    if abstract == None:
                        abstract = response.xpath('/html/body/div[3]/div[1]/div[2]/p[3]/text()').extract_first()
                        if abstract == None:
                            abstract = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[3]/p[1]/text()').extract_first()
                            if abstract == None:
                                abstract = response.xpath('/html/body/div[3]/div[1]/div[2]/p[2]/text()').extract_first()
                                if abstract == None:
                                    abstract = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[3]/p[3]/span/text()').extract_first()
                                    if abstract == None:
                                        abstract = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[3]/p[4]/text()').extract_first()
        # print(abstract)
        images = response.xpath('/html/body/div[1]/div[2]/div[1]/div/div[3]/p/img/@src').extract()

        category1 = response.xpath('/html/body/div[1]/div[1]/div[2]/div/div[2]/ul/li[3]/a/text()').extract_first()
        if category1 == None:
            category1 = 'Notícias'

        item['title'] = title
        item['body'] = body
        item['abstract'] = abstract
        item['images'] = images
        item['category1'] = category1
        item['pub_time'] = pub_time

        yield item






