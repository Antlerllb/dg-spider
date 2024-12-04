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



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class SarabanSpider(BaseSpider):
    name = 'saraban'
    website_id = 2279
    language_id = 1779
    author = '刘雨鑫'
    lan_num = 1
    base_url = 'https://sarabangla.net/archive/'

    @staticmethod
    def gain_detail_time(fault_time, flag):
        i = int(fault_time.split(':')[0])
        if flag == 'pm':
            i = i + 12
        if i == 24:
            i = 0
        detail_time = str(i).zfill(2) + ':' + fault_time.split(':')[1].zfill(2) + ':00'
        return detail_time

    @staticmethod
    def time_fix(time_list):
        month = str(OldDateUtil.EN_1866_DATE[time_list[2]]).zfill(2)
        prefix_time = f'{time_list[3]}-{month}-{time_list[1].zfill(2)}'
        first_time = prefix_time + ' ' + SarabanSpider.gain_detail_time(time_list[4], time_list[5])
        return prefix_time, first_time

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
        body = SarabanSpider.clear_none(SarabanSpider.clear(body))
        body = SarabanSpider.clear(body)
        title = SarabanSpider.clear_none(SarabanSpider.clear(title))
        if abstract != '':
            abstract = SarabanSpider.clear_none(SarabanSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def start_requests(self):
        yield scrapy.Request(self.base_url, callback=self.parse)

    def parse(self, response):
        block = response.xpath('//div[@class="col-lg-8 col-md-12"]//div[@class="row"]')
        prefix_time = ''
        for i in block:
            time_list = i.xpath('.//ul[@class="post-meta ul-inline"]/li/small/text()').extract_first().split(' ')
            if len(time_list) == 7:
                prefix_time, pub_time = self.time_fix(time_list)
            else:
                pub_time = prefix_time + ' ' + self.gain_detail_time(time_list[2], time_list[3])
            if OldDateUtil.time is not None and OldDateUtil.time >= OldDateUtil.str_datetime_to_timestamp(pub_time):
                return
            detail_url = i.xpath('.//h4/strong/a/@href').extract_first()
            title = i.xpath('.//h4/strong/a/text()').extract_first()
            images = []
            image = i.xpath('.//img/@src').extract_first()
            if image is not None:
                images.append(image)
            response.meta['pub_time'] = pub_time
            response.meta['title'] = title
            response.meta['images'] = images
            yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)
        next_url = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_url is None:
            return
        yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        pub_time = response.meta['pub_time']
        title = response.meta['title']
        images = response.meta['images']
        category1 = response.xpath('//div[@class="post-category"]/span/text()').extract_first()
        abstract = ''
        body = ''
        p_list = response.xpath('//div[@class="single_content"]//p')
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


