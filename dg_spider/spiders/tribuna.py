


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
class TribunaSpider(BaseSpider):
    name = 'tribuna'
    website_id = 1293
    language_id = 2181
    start_urls = ['http://www.tribuna.cu/archivo']
    is_http = 1

    def parse(self, response):
        flag = True
        articles = response.xpath('//div[@class="col-md-12 g-searchpage-results"]//article')
        meta = response.meta
        if OldDateUtil.time is not None:
            t = articles[-1].xpath('.//p[@class="author-date"]/text()').get().replace("@", "").split(" ")
            last_time = "{}-{}-{}".format(t[4], Spanish_MONTH[t[2]], t[0]) + ' ' + t[5]
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.xpath('.//p[@class="author-date"]/text()').get().replace("@", "").split(" ")
                pub_time = "{}-{}-{}".format(tt[4], Spanish_MONTH[tt[2]], tt[0]) + ' ' + tt[5]
                article_url = 'http://www.tribuna.cu/' + article.xpath('.//h2[@class="notice-title-l2"]/a/@href').get()
                title = article.xpath('.//h2[@class="notice-title-l2"]/a/text()').get()
                meta['data'] = {
                    'pub_time': pub_time,
                    'title': title,
                    'category1': article_url.split("/")[3]
                }
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath('//li[@class="next_page"]/a/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath('//li[@class="next_page"]/a/@href').get()
                yield Request(url=next_page, callback=self.parse, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//div[@class="article-text"]/p')] if paragraph.strip() != '' and paragraph.strip() != '\xa0']
        )
        item['abstract'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//div[@class="notice-summary mt-10 mb-10"]/p')] if paragraph.strip() != '' and paragraph.strip() != '\xa0']
        )
        if item['abstract'] == "":
            item['abstract'] = item['body'].split('\n')[0]
        item['images'] = ['http://www.tribuna.cu'+i for i in response.xpath('//div[@class="blog-item-body"]//img/@src').getall()]

        return item