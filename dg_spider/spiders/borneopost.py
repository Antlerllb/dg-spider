# encoding: utf-8




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re

month = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }
# check:wpf pass
# author  马颢源
class borneopostSpider(BaseSpider):
    name = 'borneopost'
    website_id = 155
    language_id = 1866
    start_urls = ['https://www.theborneopost.com']


    def parse(self, response):
        li = response.xpath('//*[@id="menu-main-menu"]/li')
        li.pop(0)
        for i in li:
            url = i.xpath('./a/@href').get()
            category1 = i.xpath('./a/text()').get()
            yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        flag = True
        if OldDateUtil.time is not None:
            time = response.xpath('/html/body/div[1]/div[4]/div[2]/div/div[2]/article[1]/div/div/div[1]/time/@datetime').get().strip()
            time = time.split("T")
            last_time = time[0] + ' 00:00:00'

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            article_list = response.xpath('//div[@class="content"]')
            for i in article_list:
                time = response.xpath('/html/body/div[1]/div[4]/div[2]/div/div[2]/article[1]/div/div/div[1]/time/@datetime').get().strip()
                time = time.split("T")
                pub_time = time[0] + ' 00:00:00'
                url= i.xpath('./a/@href').get()
                response.meta['abstract'] = i.xpath('.//p/text()').get()
                response.meta['title'] = i.xpath('./a/text()').get().strip()
                response.meta['images'] = i.xpath('//div[@class="post-wrap"]/a/img/@src').get()
                response.meta['pub_time'] = pub_time
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = response.xpath('//a[@class="next page-numbers"]/@href').extract()[0]
            if next_page:
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)  # 默认回调给parse()
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        try:
            item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@class="post-content description "]/p')])
        except:
            item['body'] = []
        item['images'] = response.meta['images']
        yield item
