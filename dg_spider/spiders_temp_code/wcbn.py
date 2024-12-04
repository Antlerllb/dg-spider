

from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


ENGLISH_MONTH = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sept': '09',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }
# author: mhy
# check:wpf pass
class wcbnSpider(BaseSpider):
    name = 'wcbn'
    start_urls = ['https://www.sccci.org.sg/']#原网页没什么可以爬的，跳转到新的网址,部分内容下没有body，数据量较少
    website_id = 201
    language_id = 2266
    #proxy = '02'

    def parse(self, response):
        url = response.xpath('//*[@id="pageHeader"]/div[3]/div/div[2]/div/nav/ul/li[3]/a/@href').get()
        category1 = response.xpath('//*[@id="pageHeader"]/div[3]/div/div[2]/div/nav/ul/li[3]/a/span/text()').get()
        yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        flag = True
        if OldDateUtil.time is not None:
            month = response.xpath('//ul[@class="event-listing clearfix"]/li[1]//div[@class="event-month"]/text()').get().strip()
            date = response.xpath('//ul[@class="event-listing clearfix"]/li[1]//div[@class="event-date"]/text()').get().strip()
            year = OldDateUtil.get_now_datetime_str().split("-")[0].strip()
            last_time = year + '-' + OldDateUtil.EN_1866_DATE[month] + '-' + date + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            article_list = response.xpath('//ul[@class="event-listing clearfix"]/li')
            for i in article_list:
                url = i.xpath('./a/@href').get()
                month = response.xpath(
                    '//ul[@class="event-listing clearfix"]/li[1]//div[@class="event-month"]/text()').get().strip()
                date = response.xpath(
                    '//ul[@class="event-listing clearfix"]/li[1]//div[@class="event-date"]/text()').get().strip()
                year = OldDateUtil.get_now_datetime_str().split("-")[0].strip()
                pub_time = year + '-' + OldDateUtil.EN_1866_DATE[month] + '-' + date + ' 00:00:00'
                response.meta['title'] = i.xpath('.//div[@class="event-title"]/text()').get()
                response.meta['images'] = i.xpath('//div[@class="eventPhoto"]/figure//img/@src').get()
                response.meta['pub_time'] = pub_time
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
              flag = False
              self.logger.info("时间截止")
        if flag:
            next_page = 'https://www.sccci.org.sg'+response.xpath('//*[@id="article-list-view"]/div/ul/li[13]/a/@href').get()
            if next_page:
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)  # 默认回调给parse()
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['abstract'] = None
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        try:
            item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@class="col-xs-12 col-sm-12 pull-left"]//p')])
        except:
            item['body'] = []
        item['images'] = response.meta['images']
        yield item
