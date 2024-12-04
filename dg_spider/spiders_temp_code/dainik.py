import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import sys


class DainikSpider(BaseSpider):
    name = 'dainik'
    bn_url = 'https://m.dainikshiksha.com/search/latest/paginate-{}/'
    en_url = 'https://m.dainikshiksha.com/en/search/latest/paginate-{}/'
    website_id = 2280
    language_id = 1779
    author = '刘雨鑫'
    bn_page = 2
    bn_page_num = 1749
    en_page_num = 8
    en_page = 2
    lan_num = 2

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
            result += i.replace('\t', '').replace('\r', '').replace('\xa0', '')
            if i != ss_list[-1]:
                result += ' '
        return result

    @staticmethod
    def correct_news(title, abstract, body):
        body = DainikSpider.clear_none(DainikSpider.clear(body))
        body = DainikSpider.clear(body)
        title = DainikSpider.clear_none(DainikSpider.clear(title))
        if abstract != '':
            abstract = DainikSpider.clear_none(DainikSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def start_requests(self):
        flag = False
        if OldDateUtil.time is not None:
            flag = True
        for en_i in range(1, self.en_page_num + 1):
            en_url = self.en_url.format(en_i)
            yield scrapy.Request(en_url, callback=self.parse, meta={'lan': 'en'})
            if flag:
                break
        for bn_i in range(1, self.bn_page_num + 1):
            bn_url = self.bn_url.format(bn_i)
            if flag and bn_i == 9:
                return
            yield scrapy.Request(bn_url, callback=self.parse, meta={'lan': 'bn'})

    def parse(self, response):
        block = response.xpath('//div[@class="col-md-6 col-sm-12"]')
        for i in block:
            images = i.xpath('./a/img/@src').extract()
            detail_url = i.xpath('./a/@href').extract_first()
            response.meta['images'] = images
            if 'en' == response.meta['lan']:
                response.meta['id'] = 1866
                response.meta['category1'] = 'Latest news'
            elif 'bn' == response.meta['lan']:
                response.meta['id'] = 1779
                response.meta['category1'] = 'সর্বশেষ সংবাদ'
            yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        pub_time = response.xpath('/html/body/div[5]/div/div/article/header/div[1]/time/@datetime').extract_first()
        if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
            return
        images = response.meta['images']
        title = response.xpath('//h1[@class="page-title"]/font/text()').extract_first()
        body = ''
        p_list = response.xpath('//div[@class="entry-content card-body"]//p | //div[@class="entry-content card-body"]//div[@style="text-align:justify"]')
        abstract = ''
        for i in p_list:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace('\n', '')
            body += p + '\n'
        title, abstract, body = self.correct_news(title, abstract, body)
        item['title'] = title
        item['abstract'] = abstract
        item['body'] = body
        item['category1'] = response.meta['category1']
        item['images'] = images
        item['pub_time'] = pub_time
        self.language_id = response.meta['id']
        if body != '':
            yield item



