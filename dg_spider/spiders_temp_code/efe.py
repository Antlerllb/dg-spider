


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy
from lxml import etree
import scrapy
import requests


# v1Author: 曾嘉祥
# v2Author: 彭雨胜 review: 彭雨胜 pass
class EfeSpider(BaseSpider):
    name = 'efe'
    website_id = 899
    language_id = 2181
    proxy = "02"
    start_urls = ['https://www.efe.com/efe/espana/1']

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//*[@class=" efe-menu-secciones dropdown"]/ul/li/a')

        for category in categories:
            page_link = 'https://www.efe.com' + category.xpath('./@href').get()
            category1 = category.xpath('./text()').get()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        flag = True
        meta = response.meta
        articles = response.xpath('//li[@class=" importante"]/article')

        if OldDateUtil.time is not None:
            last_article_url = 'https://www.efe.com' + articles[-1].xpath('./a/@href').get()
            tree = etree.HTML(requests.get(url=last_article_url, timeout=5).text)
            last_time = tree.xpath('//time/@datetime')[0].replace('T', ' ').replace('Z', '')

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = 'https://www.efe.com' + article.xpath('./a/@href').get()
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")

        if flag:
            if response.xpath('//link[@rel="next"]/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = 'https://www.efe.com' + response.xpath('//link[@rel="next"]/@href').get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = response.xpath('//div[@id="div_guia"]/text()').get()
        item['title'] = response.xpath('//h1[@id="div_titulo"]/text()').get()
        item['pub_time'] = response.xpath('//time/@datetime').get().replace('T', ' ').replace('Z', '')
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//div[@id="div_texto"]//p')]]
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = [response.xpath('//div[@class="slide foto selected"]//img/@src').get()]
        return item
