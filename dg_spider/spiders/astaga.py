


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy


# author : 彭雨胜
class AstagaSpider(BaseSpider):
    name = 'astaga'
    website_id = 33
    language_id = 1952
    start_urls = ['https://astaga.com/']

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//*[@id="tdi_50"]/div/ul/li/a')
        for category in categories[1: -1]:
            page_link = category.xpath('./@href').get()
            category1 = category.xpath('./div/text()').get()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        flag = True
        articles = response.xpath('//div[@id="tdi_102"]/div')
        meta = response.meta
        if OldDateUtil.time is not None:
            t = articles[-1].xpath('.//time/text()').get().replace(',', '').split(' ')
            last_time = "{}-{}-{}".format(t[2], str(OldDateUtil.EN_1866_DATE[t[0]]).zfill(2), t[1]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.xpath('.//time/text()').get().replace(',', '').split(' ')
                pub_time = "{}-{}-{}".format(tt[2], str(OldDateUtil.EN_1866_DATE[tt[0]]).zfill(2), tt[1]) + ' 00:00:00'
                article_url = article.xpath('.//h3/a/@href').get()
                title = article.xpath('.//h3/a/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath(
                    '//div[@class="page-nav td-pb-padding-side"]//a[@aria-label="next-page"]/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath(
                    '//div[@class="page-nav td-pb-padding-side"]//a[@aria-label="next-page"]/@href')
                yield Request(url=next_page.get(), callback=self.parse_page, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//*[@id="tdi_110"]/div/div[1]/div/div[@data-td-block-uid="tdi_115"]/div/div')]]
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = [response.xpath('//*[@id="tdi_90"]/div/div/div/div[2]/div[2]/img/@src').get()]
        return item
