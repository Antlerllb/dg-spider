


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class JornaldeangolaSpider(BaseSpider):  # 类名重命名
    author = '刘雨鑫'
    name = 'jornaldeangola'  # name的重命名
    website_id = 2070
    language_id = 2122
    start_urls = ['https://www.jornaldeangola.ao/ao/']

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
        li_list = response.xpath('//*[@id="collapsibleNavId"]/ul/li[1]/following-sibling::*')
        for li in li_list:
            url = li.xpath('./a/@href').extract_first()
            if url is not None and 'noticias' in url:
                response.meta['class_url'] = 'https://www.jornaldeangola.ao' + url
                yield scrapy.Request(response.meta['class_url'], callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        block = response.xpath(
            '//div[@class="row"]//div[@class="col-lg-3 "] | //div[@class="row"]//div[@class="col-lg-3 opniao"]'
            )
        for i in block:
            time_list = i.xpath('.//div[@class="data"]/span/text()').extract_first().split('/')
            pub_time = f'{time_list[2]}-{time_list[1]}-{time_list[0]} 12:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            response.meta['pub_time'] = pub_time
            response.meta['title'] = i.xpath('.//h2/text()').extract_first()
            response.meta['abstract'] = i.xpath('.//p/text()').extract_first()
            detail_url = 'https://www.jornaldeangola.ao' + i.xpath('./div/a/@href').extract_first()
            yield scrapy.Request(
                detail_url,
                callback=self.parse_item, meta=response.meta
                )
        next_url = response.xpath('//li[@class="page-item page-next"]/a/@href').extract_first()
        if next_url is None:
            return
        yield scrapy.Request(
            'https://www.jornaldeangola.ao' + next_url, callback=self.parse_page, meta=response.meta
            )

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['abstract'] = response.meta['abstract']
        item['category1'] = response.xpath('//div[@class="tag mb-3"]/text()').extract_first()
        image = response.xpath('//div[@class="imagem-detalhe"]/img/@src').extract()
        if len(image) != 0:
            item['images'] = ['https://www.jornaldeangola.ao' + image[0]]
        body = ''
        tag_span = response.xpath('//div[@class="body-news"]/span//text()').extract()
        for i in tag_span:
            body += i.replace('\r\n', '')
        tag_p = response.xpath('//div[@class="body-news"]//p')
        if len(tag_p) == 0:
            p = ''
            tag = response.xpath('//div[@class="body-news"]//text()').extract()
            for i in tag:
                p += i.replace('\t', '').replace('\n', '') + '\n'
            t_body = self.clear_none(self.clear(p))
        else:
            for i in tag_p:
                p = ''
                for j in i.xpath('.//text()').extract():
                    p += j.replace('\r\n', '').replace('\n', '')
                body += p + '\n'
            t_body = self.clear_none(self.clear(body.replace('\t', '')))
        if len(t_body.split('\n')) == 1:
            t_body = response.meta['abstract'] + '\n' + t_body
        item['body'] = t_body
        yield item
