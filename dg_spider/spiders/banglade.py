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

import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import datetime
import scrapy
import time
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


class BangladeSpider(BaseSpider):
    name = 'banglade'
    author = '刘雨鑫'
    website_id = 2266
    language_id = 1779
    # start_urls = ['https://bangladeshinfo.com/', 'https://bn.bangladeshinfo.com']
    en_url = 'https://bangladeshinfo.com/archive/{}'
    bn_url = 'https://bn.bangladeshinfo.com/archive/{}'
    lan_num = 2

    @staticmethod
    def translate(time_list):
        lst = time_list
        month = str(OldDateUtil.EN_1866_DATE[lst[1]])
        detail_time = lst[4].split(':')[0].zfill(2) + ':' + lst[4].split(':')[1]
        if lst[5] == 'PM':
            i = int(lst[4].split(':')[0]) + 12
            if i == 24:
                i = '00'
            detail_time = str(i) + ':' + lst[4].split(':')[1]
        pub_time = f'{lst[3]}-{month.zfill(2)}-{lst[2].zfill(2)} {detail_time}:00'
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
        body = BangladeSpider.clear_none(BangladeSpider.clear(body))
        body = BangladeSpider.clear(body)
        title = BangladeSpider.clear_none(BangladeSpider.clear(title))
        if abstract != '':
            abstract = BangladeSpider.clear_none(BangladeSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def start_requests(self):
        today = datetime.date.today()
        day = today
        dt = ''
        if OldDateUtil.time is not None:
            time_local = time.localtime(OldDateUtil.time)
            dt = str(time.strftime("%Y-%m-%d", time_local))
        while True:
            if str(day) == '2018-12-01' or str(day) == dt:
                return
            en_url = self.en_url.format(str(day))
            bn_url = self.bn_url.format(str(day))
            yield scrapy.Request(en_url, callback=self.parse)
            yield scrapy.Request(bn_url, callback=self.parse)
            day = day - datetime.timedelta(days=1)

    def parse(self, response):
        block = response.xpath('//div[@class="news"]//div[@class="item"]')
        for i in block:
            detail_url = response.request.url.split('/archive')[0] + i.xpath('./div[2]/p/a/@href').extract_first()
            images = []
            image = i.xpath('./div[1]/a/img/@src').extract_first()
            if image is not None:
                images.append(image)
            abstract = i.xpath('./div[2]/p/a/text()').extract_first()
            response.meta['images'] = images
            response.meta['abstract'] = abstract
            yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.xpath('//div[@class="content"][1]/h3/strong/text()').extract_first()
        images = response.meta['images']
        abstract = response.meta['abstract']
        time_list = response.xpath('//div[@class="post-meta-date"]/text()').extract()[1].replace('\n', '').replace(',', '').split(' ')
        pub_time = self.translate(time_list)
        category1 = 'archive'
        body = ''
        p_list = response.xpath('//div[@class="content"][2]//p')
        # print(p_list)
        for i in p_list:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace('\n', '')
            if p != '':
                body += p + '\n'
        # print(body)
        title, abstract, body = self.correct_news(title, abstract, body)
        # print(body)
        item['title'] = title
        item['abstract'] = abstract
        item['body'] = body
        item['category1'] = category1
        item['images'] = images
        item['pub_time'] = pub_time
        if 'bn' in response.request.url:
            self.language_id = 1779
        else:
            self.language_id = 1866
        if body != '':
            yield item


