


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
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
class Periodico26Spider(BaseSpider):
    name = 'periodico26'
    website_id = 1295
    language_id = 2181
    start_urls = ['http://www.periodico26.cu/index.php/es']
    is_http = 1

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//ul[@class="nav menu  nav-pills mod-list"]/li/a')
        for category in categories[1:-2]:
            page_link = 'http://www.periodico26.cu' + category.xpath('./@href').get()
            category1 = category.xpath('./text()').get().strip()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        flag = True
        articles = response.xpath('//div[@class="blog"]/div/div[@class="span12"]')
        meta = response.meta

        if OldDateUtil.time is not None:
            tt = articles[-1].xpath('.//time/@datetime').get().replace("T", " ").split("+")[0].split("-")
            last_time = "{}-{}-{}".format(tt[0], tt[1], tt[2])
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                if article.xpath('.//time/@datetime').get():
                    t = article.xpath('.//time/@datetime').get().replace("T", " ").split("+")[0].split("-")
                    pub_time = "{}-{}-{}".format(t[0], t[1], t[2])
                    article_url = article.xpath('.//div[@class="page-header"]/h2/a/@href').get()
                    title = article.xpath('.//div[@class="page-header"]/h2/a/text()').get().strip()
                    meta['data']['pub_time'] = pub_time
                    meta['data']['title'] = title
                    yield Request(url='http://www.periodico26.cu' + article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath('//a[@title="Siguiente"]/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = 'http://www.periodico26.cu' + response.xpath('//a[@title="Siguiente"]/@href').get()
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
                '//div[@itemprop="articleBody"]/p')] if paragraph.strip() != '' and paragraph.strip() != '\xa0']
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = ['http://www.periodico26.cu' + i for i in response.xpath('//div[@class="item-page"]//img/@src').getall()]
        return item