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
import datetime
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
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


class DhakaSpider(BaseSpider):
    name = 'dhaka'
    author = '刘雨鑫'
    lan_num = 1
    website_id = 2277
    language_id = 1779
    base_url = 'https://www.dhakatimes24.com/archive/online-edition/{}'

    # start_urls = 'https://www.dhakatimes24.com'
    @staticmethod
    def translate_time(time_list):
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
                    # if j == i.split(':')[0] and lst[4] == 'পিএমণ':
                    #     z = str(int(z) + 12)
                    detail_time += z + ':'
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
        body = DhakaSpider.clear_none(DhakaSpider.clear(body))
        body = DhakaSpider.clear(body)
        title = DhakaSpider.clear_none(DhakaSpider.clear(title))
        if abstract != '':
            abstract = DhakaSpider.clear_none(DhakaSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def start_requests(self):
        dt = ''
        if OldDateUtil.time is not None:
            time_local = time.localtime(OldDateUtil.time)
            dt = str(time.strftime("%Y-%m-%d", time_local))
        today = datetime.date.today()
        day = today
        while True:
            if str(day) == '2016-12-31' or str(day) == dt:
                return
            url = self.base_url.format(str(day).replace('-', '/'))
            yield scrapy.Request(url, callback=self.parse)
            day = day - datetime.timedelta(days=1)

    def parse(self, response):
        div_list = response.xpath('//div[@class="col-md-6 col-sm-6"]')
        for div in div_list:
            response.meta['category1'] = div.xpath('.//h4/text()').extract_first()
            urls = div.xpath('.//li/a/@href').extract()
            for url in urls:
                yield scrapy.Request(url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        category1 = response.meta['category1']
        title = response.xpath('//div[@class="headline_section"]/h1/text()').extract_first()
        time_ll = response.xpath('//div[@class="rpt_name"][2]/text()').extract_first().replace('\xa0', ' ').replace(',', '').strip(' ').split(' | ')[0].split(': ')
        time_list = time_ll[1].split(' ')
        pub_time = self.translate_time(time_list)
        images = []
        image_lst = response.xpath('//div[@class="dtl_section"]//img')
        for i in image_lst:
            image = i.xpath('./@src').extract_first()
            if image is not None:
                if not image.startswith('http'):
                    image = 'https://www.dhakatimes24.com' + image
                images.append(image)
        body = ''
        abstract = ''
        p_list = response.xpath('//div[@class="dtl_section"]//p')
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

