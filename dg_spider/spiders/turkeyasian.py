# encoding: utf-8



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


# author: 张珍珍
class TrtNetTrSpider(BaseSpider):
    name = 'turkeyasian'
    allowed_domains = ['turkeyasian.com']
    start_urls = ['https://turkeyasian.com/']

    website_id = 1953
    language_id = 1813

    def parse(self, response):
        li_list = response.xpath('//div[@class="menu-main-menu-container"]/ul/li')[1:-2]
        for i in li_list:
            url = i.xpath('./a/@href').get()
            category1 = i.xpath('./a/text()').get()
            yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        flag = True
        if OldDateUtil.time is not None:
            time = response.xpath('//span[@class="mh-meta-date updated"]/text()').get().split()
            last_time = time[0] + '-' + time[2] + '-' + time[4] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            article_list = response.xpath('//div[@id="main-content"]/article')
            for i in article_list:
                url = i.xpath('./figure/a/@href').get()
                time = response.xpath('//span[@class="mh-meta-date updated"]/text()').get().split()
                pub_time = time[0] + '-' + time[2] + '-' + time[4] + ' 00:00:00'
                response.meta['title'] = i.xpath('./figure/a/img/@alt').get().strip()
                response.meta['abstract'] = i.xpath('.//div[@class="mh-excerpt"]/p/text()').get().strip()
                response.meta['images'] = i.xpath('./figure/a/img/@data-src').get()
                response.meta['pub_time'] = pub_time
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
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
        item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//p[@class="has-medium-font-size"]')[:-1]])
        try:
            item['images'] = [i.xpath('./@data-src').get() for i in response.xpath('//figure[@class="entry-thumbnail"]/img')]
        except:
            item['images'] = []
        yield item
