# encoding: utf-8




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re


month = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }
# check:wpf pass
#author 马颢源
class modgovSpider(BaseSpider):
    name = 'modgov'
    website_id = 390
    language_id = 2036
    start_urls = ['https://www.mod.gov.my/ms/']

    def parse(self, response):
        li = response.xpath('//div[@id="menu-6682-particle"]/nav/ul/li[5]/ul/li/div/div/ul/li[2]/a')
        url = 'https://www.mod.gov.my' + li.xpath('./@href').get()
        category1 = li.xpath('./span/span/text()').get()
        yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        flag = True
        if OldDateUtil.time is not None:
            time = response.xpath('//*[@id="g-copyright"]//div[@class="db8sitelastmodifiedvisible-desktop"]/text()').get().strip()
            time = re.sub(r'[^\w\s]','',time)
            time = time.split(" ")
            last_time = time[5] + '-' + month[time[4]] + '-' + time[3] + ' 00:00:00'

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            article_list = response.xpath('//div[@class="span6"]')
            for i in article_list:
                time = response.xpath(
                    '//*[@id="g-copyright"]//div[@class="db8sitelastmodifiedvisible-desktop"]/text()').get().strip()
                time = re.sub(r'[^\w\s]', '', time)
                time = time.split(" ")
                pub_time = time[5] + '-' + month[time[4]] + '-' + time[3] + ' 00:00:00'
                url = 'https://www.mod.gov.my' + i.xpath('.//h2/a/@href').get()
                response.meta['abstract'] = i.xpath('.//p/text()').get()
                response.meta['title'] = i.xpath('.//h2/a/text()').get().strip()
                response.meta['images'] = 'https://www.mod.gov.my/ms/mediamenu'+ i.xpath('.//img/@src').get()
                response.meta['pub_time'] = pub_time
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间 截止")
        if flag:
            next_page = 'https://www.mod.gov.my' + response.xpath('//li[@class="pagination-next"]/a/@href').get()
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
            item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@itemprop="articleBody"]//p')])
        except:
            item['body'] = None
        item['images'] = response.meta['images']
        yield item
