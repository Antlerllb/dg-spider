from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil



import re


class LahoraclSpider(BaseSpider):  # 类名重命名
    author = '刘雨鑫'
    name = 'lahoracl'  # name的重命名
    website_id = 1328  # id一定要填对！
    lan_num = 1
    language_id = 2181  # id一定要填对！
    start_urls = ['https://lahora.cl/']
    emoji_pattern = re.compile(
        u"(\ud83d[\ude00-\ude4f])|"  # emoticons
        u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
        u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
        u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
        u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
        "+", flags=re.UNICODE
        )

    @staticmethod
    def remove_emoji(text):
        return LahoraclSpider.emoji_pattern.sub(r'', text)

    @staticmethod
    def clear(ss):
        f_list = []
        for i in ss.split('\n'):
            if i != '':
                f_list.append(i)
        result = ''
        for i in f_list:
            result += i
            if i != f_list[-1]:
                result += '\n'
        return result

    @staticmethod
    def clear_none(ss):
        ss_list = [i for i in ss.split(' ') if i != '']
        result = ''
        for i in ss_list:
            result += i
            if i != ss_list[-1]:
                result += ' '
        return result

    def parse(self, response):
        block = response.xpath('//*[@id="sidebar"]/div[1]/ul//li')
        for i in block:
            response.meta['class_url'] = 'https://lahora.cl' + i.xpath('./a/@href').extract_first()
            yield scrapy.Request(response.meta['class_url'], callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        block = response.xpath('//section[@class="listado"]//article')
        time_list = block[0].xpath('./div[1]/a/@href').extract_first().split('/')
        first_time = f'{time_list[-5]}-{time_list[-4]}-{time_list[-3]} 12:00:00'
        if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(first_time) < OldDateUtil.time:
            return
        for i in block:
            time_list = i.xpath('./div[1]/a/@href').extract_first().split('/')
            pub_time = f'{time_list[-5]}-{time_list[-4]}-{time_list[-3]} 12:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            response.meta['title'] = i.xpath('./div[1]/a/@title').extract_first()
            response.meta['image_out'] = i.xpath('./div[1]/a/img/@src').extract()
            response.meta['pub_time'] = pub_time
            detail_url = i.xpath('./div[1]/a/@href').extract_first()
            yield scrapy.Request(
                detail_url,
                callback=self.parse_item, meta=response.meta
                )
        next_url = response.xpath('//div[@class="paginacion"]/a[last()]/@href').extract_first()
        if next_url is None:
            return
        yield Request(next_url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        body = ''
        tag = response.xpath(
            '//div[@class="the-content"]//p[@class="whitespace-pre-wrap"] | //div[@class="the-content"]//p'
            )
        for i in tag:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace('\n', '').replace(' ', '')
            body += p + '\n'
        body = self.clear_none(self.clear(body))
        item['pub_time'] = response.meta['pub_time']
        item['title'] = response.meta['title']
        item['category1'] = response.xpath('//article[@class="principal"]/h2/a/@title').extract_first()
        abstract = response.xpath('/html/body/div[7]/div/main/article/p/text()').extract_first()
        images = response.meta['image_out']
        image_in = response.xpath('//div[@class="the-content"]//img[@loading="lazy"]/src').extract()
        if len(image_in) != 0:
            images += image_in
        item['images'] = images
        if body == '':
            body = item['title']
        if len(body.split('\n')) == 1 and abstract is not None:
            body = abstract + '\n' + body
        if len(body.split('\n')) == 1 and abstract is None:
            body = item['title'] + '\n' + body
        if abstract is None:
            abstract = body.split('\n')[0]
        abstract = self.remove_emoji(abstract)
        abstract = abstract.replace('💯', '')
        item['abstract'] = self.clear_none(self.clear(abstract))
        item['body'] = self.clear_none(self.clear(body))
        yield item
