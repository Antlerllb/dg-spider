


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy


# author : 彭雨胜
# check :魏芃枫
class ElmundoSpider(BaseSpider):
    name = 'elmundo'
    website_id = 1276
    language_id = 2181
    start_urls = ['https://www.elmundo.es/']

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//*[@class="ue-c-main-navigation__body"]//ul/li')
        for category in categories:
            page_link = category.xpath('.//a/@href').get()
            category1 = category.xpath('.//a//text()').get()
            if category1 == ' ':
                category1 = page_link.split('/')[-1].split('.')[0]
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        flag = True
        meta = response.meta
        if response.xpath('//div[@class="ue-l-cover-grid__unit ue-l-cover-grid__unit--no-grow"]/article'):
            articles = response.xpath('//div[@class="ue-l-cover-grid__unit ue-l-cover-grid__unit--no-grow"]/article')
            if OldDateUtil.time is not None:
                last_time = articles[-1].xpath('.//div[@class="ue-c-cover-content__published-date"]/@data-publish').get()
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                for article in articles:
                    pub_time = article.xpath('.//div[@class="ue-c-cover-content__published-date"]/@data-publish').get()
                    article_url = article.xpath('./a/@href').get()
                    category2 = article.xpath('.//*[@class="ue-c-cover-content__kicker"]//text()').get()
                    title = article.xpath('.//h2//text()').get()
                    meta['data']['pub_time'] = pub_time
                    meta['data']['title'] = title
                    meta['data']['category2'] = category2
                    yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
            else:
                flag = False
                self.logger.info("时间截止")
            # 翻页
            if flag:
                if response.xpath('//div[@class="ue-c-pagination__item ue-c-pagination__item--next"]/a/@href').get() is None:
                    self.logger.info("到达最后一页")
                else:
                    next_page = response.xpath('//div[@class="ue-c-pagination__item ue-c-pagination__item--next"]/a/@href')
                    yield Request(url=next_page.get(), callback=self.parse_page, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = meta['data']['category2']
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']

        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//div[@class="ue-l-article__body ue-c-article__body"]/p | //div[@itemprop="articleBody"]/p | //dl['
                '@class="ue-c-article__interview"]/dd | //dl[@class="ue-c-article__interview"]/dt | //div[@class="row '
                'content cols-30-70"]/p | //article//p | //div[@class="articleContent .p-large fb-quotable"]/p | '
                '//div[@class="body provincia"]/p | //div[@class="article"]/p')]]
        )
        item['abstract'] = item['body'].split('\n')[0]
        if item['abstract'] is None or item['abstract'] == "":
            item['abstract'] = item['body'].split('\n')[1]
        item['images'] = response.xpath('//img[@class="ue-c-article__image"]/@src | //div[@itemprop="articleBody"]//img/@href | //picture/img/@href').getall()
        return item
