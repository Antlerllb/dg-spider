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


class VenezuelaSpider(BaseSpider):
    name = "venezuela"
    website_id = 1323
    language_id = 2181
    author = '刘雨鑫'
    i = 1
    lan_num = 1
    topic_urls = ['https://www.24venezuela.com/noticias/presos-politicos/?page=1',
                  'https://www.24venezuela.com/noticias/oposicion/?page=1',
                  'https://www.24venezuela.com/noticias/gobierno/?page=1',
                  'https://www.24venezuela.com/noticias/asamblea-nacional/?page=1',
                  'https://www.24venezuela.com/noticias/crisis-economica/?page=1',
                  'https://www.24venezuela.com/noticias/empresas-y-prductos/?page=1',
                  'https://www.24venezuela.com/noticias/regimen-cambiario/?page=1',
                  'https://www.24venezuela.com/noticias/petroleo/?page=1',
                  'https://www.24venezuela.com/noticias/latinoamerica/?page=1',
                  'https://www.24venezuela.com/noticias/medio-oriente/?page=1',
                  'https://www.24venezuela.com/noticias/europa/?page=1',
                  'https://www.24venezuela.com/noticias/ee-uu/?page=1',
                  'https://www.24venezuela.com/noticias/beisbol/?page=1',
                  'https://www.24venezuela.com/noticias/futbol/?page=1',
                  'https://www.24venezuela.com/noticias/baloncesto/?page=1',
                  'https://www.24venezuela.com/noticias/motories/?page=1',
                  'https://www.24venezuela.com/noticias/tenis/?page=1',
                  'https://www.24venezuela.com/noticias/hipismo/?page=1',
                  'https://www.24venezuela.com/noticias/variedades/?page=1',
                  'https://www.24venezuela.com/noticias/cine/?page=1',
                  'https://www.24venezuela.com/noticias/teatro/?page=1',
                  'https://www.24venezuela.com/noticias/musica/?page=1',
                  'https://www.24venezuela.com/noticias/television/?page=1',
                  'https://www.24venezuela.com/noticias/literatura/?page=1',
                  'https://www.24venezuela.com/noticias/arte/?page=1',
                  'https://www.24venezuela.com/noticias/servicios/?page=1',
                  'https://www.24venezuela.com/noticias/protestas/?page=1',
                  'https://www.24venezuela.com/noticias/educacion/?page=1',
                  'https://www.24venezuela.com/noticias/salud/?page=1',
                  'https://www.24venezuela.com/noticias/crisis-humanitaria/?page=1']

    def start_requests(self):
        first_time = '2020-01-01 00:00:00'
        if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(first_time):
            return
        for url in self.topic_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'class_url': url})

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
        body = VenezuelaSpider.clear_none(VenezuelaSpider.clear(body))
        title = VenezuelaSpider.clear_none(VenezuelaSpider.clear(title))
        if abstract != '':
            abstract = VenezuelaSpider.clear_none(VenezuelaSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def parse(self, response):
        block = response.xpath('/html/body/div[1]/div[3]/div/div/div/following-sibling::div')
        for i in block:
            time_list = i.xpath('./div/div[2]/div/span[2]/text()').extract_first().replace(',', '').split(' ')
            if len(time_list) != 5:
                continue
            if len(time_list[3].split(':')) == 1:
                time_list[3] = time_list[3] + ':00'
            if time_list[4] == 'p.m.':
                if int(time_list[3].split(':')[0]) == 12:
                    detail_time = '00' + ':' + time_list[3].split(':')[1]
                else:
                    detail_time = str(int(time_list[3].split(':')[0]) + 12) + ':' + time_list[3].split(':')[1]
            else:
                detail_time = time_list[3].split(':')[0].zfill(2) + ':' + time_list[3].split(':')[1]
            pub_time = f'{time_list[2]}-{str(OldDateUtil.EN_1866_DATE[time_list[0][:3]]).zfill(2)}-{time_list[1].zfill(2)} {detail_time}:00'
            if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
                return
            response.meta['pub_time'] = pub_time
            response.meta['title'] = i.xpath('./div/div[2]/h4/a/text()').extract_first()
            response.meta['abstract'] = i.xpath('./div/div[2]/p/text()').extract_first()
            detail_url = 'https://www.24venezuela.com' + i.xpath('./div/div[2]/h4/a/@href').extract_first()
            response.meta['category1'] = detail_url.split('/')[-2]
            yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)
        next_page = response.xpath('/html/body/div[1]/div[3]/div/div/ul//li[last()]/a/@href').extract_first()
        if next_page is None:
            return
        next_url = response.request.url.split('/?')[0] + '/' + next_page
        yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.meta['title']
        abstract = response.meta['abstract']
        category1 = response.meta['category1']
        pub_time = response.meta['pub_time']
        images = []  # 该网页新闻无图片
        body = ''
        br_list = response.xpath('/html/body/div[1]/div[3]/div/div[2]/div[1]/p/text()').extract()
        for i in br_list:
            body += i + '\n'
        title, abstract, body = self.correct_news(title, abstract, body)
        item['title'] = title
        item['abstract'] = abstract
        item['body'] = body
        item['category1'] = category1
        item['images'] = images
        item['pub_time'] = pub_time
        yield item


