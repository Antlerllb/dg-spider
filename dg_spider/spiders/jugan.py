import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class JuganSpider(BaseSpider):
    name = 'jugan'
    author = '刘雨鑫'
    website_id = 2281
    language_id = 1779
    lan_num = 1
    topic_urls = ['https://www.jugantor.com/all-news/national',
                  'https://www.jugantor.com/all-news/job-seek', 'https://www.jugantor.com/all-news/tech',
                  'https://www.jugantor.com/all-news/lifestyle', 'https://www.jugantor.com/all-news/campus',
                  'https://www.jugantor.com/all-news/entertainment',
                  'https://www.jugantor.com/all-news/sports', 'https://www.jugantor.com/all-news/international',
                  'https://www.jugantor.com/all-news/economics', 'https://www.jugantor.com/all-news/politics']

    @staticmethod
    def translate(time_list):
        lst = time_list
        day = ''
        month = ''
        year = ''
        for i in lst:
            if i == lst[1]:
                z_month = i.replace(',', '')
                month = str(
                    OldDateUtil.BN_1779_DATE[
                        z_month.replace('ফেব্রুয়ারি', 'ফেব্রুয়ারি').replace('জানুয়ারি', 'জানুয়ারি')]
                    )
            elif i == lst[0]:
                for j in i:
                    if j != ':':
                        n = str(OldDateUtil.BN_1779_DATE[j])
                        day += n
            elif i == lst[2]:
                for j in i:
                    if j != ':':
                        n = str(OldDateUtil.BN_1779_DATE[j])
                        year += n
        pub_time = f'{year}-{month.zfill(2)}-{day} 00:00:00'
        return pub_time

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
        body = JuganSpider.clear_none(JuganSpider.clear(body))
        body = JuganSpider.clear(body)
        title = JuganSpider.clear_none(JuganSpider.clear(title))
        if abstract != '':
            abstract = JuganSpider.clear_none(JuganSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def start_requests(self):
        for class_url in self.topic_urls:
            yield scrapy.Request(class_url, callback=self.parse, meta={'category1': class_url.split('/')[-1]})

    # def parse(self, response):
    #     li_list = response.xpath(
    #         '//ul[@class="navbar-nav nav-hover mx-auto"]//li[@class="nav-item d-lg-none d-xl-block"]'
    #         )
    #     for li in li_list:
    #         url = li.xpath('./a/@href').extract_first()
    #         yield scrapy.Request(url, callback=self.parse_class, meta=response.meta)

    # def parse_class(self, response):
    #     class_url = response.xpath(
    #         '//ol[@class="breadcrumb bg-white px-0 pb-0 rounded-0"]//li[last()]/a/@href'
    #         ).extract_first()
    #     if 'all-news' in class_url:
    #         print(class_url)
            # response.meta['category1'] = class_url.split('/')[-1]
            # yield scrapy.Request(class_url, callback=self.parse_page, meta=response.meta)

    def parse(self, response):
        block = response.xpath('//div[@class="col mb-2"]')
        for i in block:
            time_list = i.xpath('.//div[@class="small text-body"]/span[2]/text()').extract_first().replace(
                ',', ''
                ).split(' ')
            pub_time = self.translate(time_list)
            if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
                return
            title = i.xpath('.//h6[@class="text-body"]/text()').extract_first()
            images = i.xpath('./div/div/a/img/@src').extract()
            response.meta['pub_time'] = pub_time
            response.meta['title'] = title
            response.meta['images'] = images
            detail_url = i.xpath('./div/div[2]/a/@href').extract_first()
            yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)
        next_url = response.xpath(
            '//ul[@class="pagination pagination-sm justify-content-end"]//li[last()]/a/@href'
            ).extract_first()
        if next_url is None:
            return
        yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.meta['title']
        category1 = response.meta['category1']
        images = response.meta['images']
        pub_time = response.meta['pub_time']
        body = ''
        abstract = ''
        p_list = response.xpath('//div[@class="IfTxty news-element-text text-justify my-2 pr-md-4 text-break"]//p')
        for i in p_list:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace('\n', '')
            body += p + '\n'
        title, abstract, body = self.correct_news(title, abstract, body)
        item['title'] = title
        item['abstract'] = abstract
        item['body'] = body
        item['category1'] = category1
        item['images'] = images
        item['pub_time'] = pub_time
        yield item


