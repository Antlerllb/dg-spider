# encoding: utf-8



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy


#   Author:叶雨婷
# 刚刚开始时403有点多，后面会好很多

class ThaipostSpider(BaseSpider):
    name = 'thaipost'
    # allowed_domains = ['thaipost.net']
    start_urls = ['https://www.thaipost.net/']
    website_id = 1657
    language_id = 2208

    def parse(self, response):
        list_pages = ["abroad/","hilight-news/","politics/","economy/","entertainment/"]
        for item in list_pages:
            meta_part = {'e': item}
            yield Request(url="https://www.thaipost.net/" + item, callback=self.get_page, meta=meta_part)

    def get_page(self, response):
        last_time = response.xpath('//div[@class="vce-posts-grid-list"]//time/@datetime').getall()[-1]
        for i in response.xpath('//div[@class="vce-posts-grid-list"]//a/@href').getall()[::2]:
            meta = {'href': i}
            yield Request(url=i, callback=self.parse_pages, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            try:
                href = response.xpath('//div[@class="vce-posts-grid-pagination"]/a[@class="vce-posts-grid-pagination-item vce-state--active"]//following-sibling::a/@href').getall()[0]
                yield Request(url="https://www.thaipost.net/" + href, callback=self.get_page)
                # print(111111)
            except AttributeError:
                pass
        # else:
        #     self.logger.info("Time Stop")


    def parse_pages(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.xpath('//h1[@class="entry-title"]/text()').getall()
        item['pub_time'] = response.xpath('//time/@datetime').getall()[0].split('T')[0] + " 00:00:00"
        item['images'] = response.xpath('//div[@class="entry-content"]//img/@src').getall()
        item['body'] = ''.join(response.xpath('//div[@class="entry-content"]//p/text()').getall())
        # print(response.xpath('//div[@class="entry-content"]//p/text()').getall())
        item['category1'] = response.meta['href'].split('/')[3]
        # 一级分类取了网址里面写的小标签，网页里没展示
        item['abstract'] = None
        item['category2'] = None

        yield item




