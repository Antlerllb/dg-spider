


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy

Spanish_MONTH = {
        'enero': '01',
        'febrero': '02',
        'marzo': '03',
        'abril': '04',
        'mayo': '05',
        'junio': '06',
        'julio': '07',
        'agosto': '08',
        'septiembre': '09',
        'octubre': '10',
        'noviembre': '11',
        'diciembre': '12'
}

# author : 彭雨胜
# check: 凌敏 pass
class GuerrilleroSpider(BaseSpider):
    name = 'guerrillero'
    website_id = 1292
    language_id = 2181
    start_urls = ['http://www.guerrillero.cu/']
    is_http = 1

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//div[@class="jeg_mainmenu_wrap"]')[1].xpath('./ul//li/a')
        for category in categories:
            page_link = category.xpath('./@href').get()
            category1 = category.xpath('./text()').get().strip()
            meta['data'] = {
                'category1': category1
            }
            if page_link != "#":
                yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        flag = True
        articles = response.xpath('//div[@class="jnews_category_content_wrapper"]//article')
        meta = response.meta
        if OldDateUtil.time is not None:
            t = articles[-1].xpath('.//div[@class="jeg_meta_date"]/a/text()').get().strip().replace(",", "").split(" ")
            last_time = "{}-{}-{}".format(t[2], Spanish_MONTH[t[0]], t[1]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.xpath('.//div[@class="jeg_meta_date"]/a/text()').get().strip().replace(",", "").split(" ")
                pub_time = "{}-{}-{}".format(tt[2], Spanish_MONTH[tt[0]], tt[1]) + ' 00:00:00'
                article_url = article.xpath('.//div[@class="jeg_meta_date"]/a/@href').get()
                title = article.xpath('.//h3[@class="jeg_post_title"]/a/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath('//a[@class="page_nav next"]/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath('//a[@class="page_nav next"]/@href').get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//div[@class="content-inner "]/p')] if paragraph.strip() != '' and paragraph.strip() != '\xa0']
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = response.xpath('//div[@class="jeg_inner_content"]//img/@src').getall()
        for i in item['images']:
            if i[0] == "d":
                item['images'].remove(i)
        # 存在纯图片情况
        if item['body'] != "":
            return item