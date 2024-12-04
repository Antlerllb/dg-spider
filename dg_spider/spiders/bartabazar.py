import scrapy
import time
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
import datetime


class BartabazarSpider(BaseSpider):
    name = 'bartabazar'
    author = '刘雨鑫'
    website_id = 2262
    language_id = 1779
    flag = False
    page_num = 322
    page = 2
    base_url = 'https://bartabazar.com/archive/'
    url = 'https://bartabazar.com/archive/page/{}/?from={}&to={}&category&division&district&upazila&keyword'
    lan_num = 1
    # 英语的新闻数量很少，并且结构不同

    @staticmethod
    def translate(time_list):
        lst = time_list
        day = ''
        month = ''
        year = ''
        detail_time = ''
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
            elif i == lst[3]:
                for j in i.split(':'):
                    z = ''
                    for k in j:
                        z += str(OldDateUtil.BN_1779_DATE[k])
                    if j == i.split(':')[0] and lst[4] == 'অপরাহ্ণ':
                        z = int(z) + 12
                        if z == 24:
                            z = 00
                    detail_time += str(z) + ':'
        pub_time = f'{year}-{month.zfill(2)}-{day} {detail_time.strip(":")}:00'
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
        body = BartabazarSpider.clear_none(BartabazarSpider.clear(body))
        body = BartabazarSpider.clear(body)
        title = BartabazarSpider.clear_none(BartabazarSpider.clear(title))
        if abstract != '':
            abstract = BartabazarSpider.clear_none(BartabazarSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if title == '':
            title = abstract
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def start_requests(self):
        if OldDateUtil.time is not None:
            day1 = datetime.date.today()
            day2 = day1 - datetime.timedelta(days=2)
            day_url = self.url.format(1, day2, day1)
            yield scrapy.Request(day_url, callback=self.parse, meta={'day1': day1, 'day2': day2, 'url': day_url})
        else:
            self.page_num = 322
            self.page = 2
            yield scrapy.Request(self.base_url, callback=self.parse)

    # def parse(self, response):
    #     # print(response.request.url)
    #     final_url = response.xpath('//ul[@class="pagination"]//li[last()]/a/@href').extract_first()
    #     if final_url is not None:
    #         self.page_num = final_url.split('page/')[1].split('/')[0]
    #         self.page = 2
    #     else:
    #         self.page_num = 2
    #         self.page = 2
    #     # print(response.meta['url'])
    #     # , meta={'page_num': page_num, 'page': page}
    #     yield scrapy.Request(response.meta['url'], callback=self.parse_page)

    def parse(self, response):
        # print(1)
        block = response.xpath('//div[@class="DTrending"]//div[@class="col-lg-4 col-12 d-flex"]')
        # print(block)
        if len(block) == 0:
            return
        for i in block:
            detail_url = i.xpath('./div/a/@href').extract_first()
            # print(detail_url)
            title = i.xpath('.//h3/text()').extract_first()
            images = []
            image = i.xpath('.//img/@src').extract_first()
            if image is not None:
                images.append(image)
            response.meta['title'] = title
            response.meta['images'] = images
            yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)
        if OldDateUtil.time is not None:
            next_url = self.url.format(self.page, response.meta['day2'], response.meta['day1'])
        else:
            next_url = 'https://bartabazar.com/archive/page/{}/'.format(self.page)
        if self.page == self.page_num:
            return
        # print(next_url)
        self.page += 1
        yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        # print(1)
        item = NewsItem(language_id=self.language_id)
        title = response.meta['title']
        category1 = response.xpath('//ol[@class="breadcrumb mt-3"]//li[2]/a/text()').extract_first()
        images = response.meta['images']
        time_list = response.xpath('//time[@class="text-black-50 text-center"]//text()').extract()[1].replace(
            ',', ''
            ).split(
            ' '
            )
        # print(time_list)
        time_list.pop(0)
        pub_time = self.translate(time_list)
        body = ''
        abstract = ''
        p_list = response.xpath('//div[@class="post-content"]//p')
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
        if body != '':
            yield item


