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


class NetraSpider(BaseSpider):
    name = 'netra'
    author = '刘雨鑫'
    website_id = 2579
    language_id = 1779
    start_urls = ['https://netra.news/']
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
        body = NetraSpider.clear_none(NetraSpider.clear(body))
        title = NetraSpider.clear_none(NetraSpider.clear(title))
        if abstract != '':
            abstract = NetraSpider.clear_none(NetraSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def parse(self, response):
        urls = []
        times = []
        tags = []
        ca_lst = []
        block = response.xpath('/html/body/div[1]/div/main/div/div//article')
        for i in block:
            time_list = i.xpath('.//time[@class="byline-meta-date"]/@datetime').extract_first().split(' ')
            pub_time = f'{time_list[2]}-{str(OldDateUtil.EN_1866_DATE[time_list[0]]).zfill(2)}-{time_list[1][:-2].zfill(2)} 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
                return
            # response.meta['pub_time'] = pub_time
            times.append(pub_time)
            category1 = i.xpath('.//div[@class="post-card-primary-tag"]/text()').extract_first()
            ca_lst.append(category1)
            detail_url = 'https://netra.news' + i.xpath('./div/a/@href').extract_first()
            urls.append(detail_url)
            tag = i.xpath('./@class').extract_first()
            tags.append(tag)
        for i in range(len(urls)):
            # if i == len(urls) - 3:
            #     return
            if 'tag-hash-en' in tags[i]:
                response.meta['id'] = 1866
            if 'tag-hash-bn' in tags[i]:
                response.meta['id'] = 1779
            response.meta['pub_time'] = times[i]
            response.meta['category1'] = ca_lst[i]
            yield scrapy.Request(urls[i], callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        pub_time = response.meta['pub_time']
        category1 = response.meta['category1']
        abstract = response.xpath('//p[@class="article-excerpt"]/text()').extract_first()
        title = response.xpath('/html/body/div[1]/div/main/article/header/h1/text()').extract_first()
        images = []
        image_lst = response.xpath('//figure[@class="article-image"]')
        for i in image_lst:
            image = i.xpath('./img/@src').extract_first()
            if image is not None:
                images.append('https://netra.news/' + image)
        body = ''
        p_list = response.xpath('/html/body/div[1]/div/main/article/section//p')
        for i in p_list:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace('\n', '')
            body += p + '\n'
        title, abstract, body = self.correct_news(title, abstract, body)
        self.language_id = response.meta['id']
        item['title'] = title
        item['abstract'] = abstract
        item['body'] = body
        item['category1'] = category1
        item['images'] = images
        item['pub_time'] = pub_time
        yield item

