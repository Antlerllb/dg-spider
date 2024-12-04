


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class SeptiemSpider(BaseSpider):
    name = 'septiem'
    author = '刘雨鑫'
    language_id = 2181
    website_id = 1302
    start_urls = ['https://www.5septiembre.cu']
    lan_num = 1

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

    @staticmethod
    def correct_news(title, abstract, body):
        title = SeptiemSpider.clear_none(SeptiemSpider.clear(title))
        if abstract != '':
            abstract = SeptiemSpider.clear_none(SeptiemSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def parse(self, response):
        li_list = response.xpath('/html/body/div[1]/header/div/nav/div/div[3]/ul/li[3]/ul//li')
        for li in li_list:
            class_url = li.xpath('./a/@href').extract_first()
            response.meta['class_url'] = class_url
            response.meta['category1'] = li.xpath('./a/text()').extract_first()
            yield scrapy.Request(class_url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        block = response.xpath('//div[@class="article-container"]//article')
        for i in block:
            time_list = i.xpath('.//span[@class="posted-on"]/a/time[1]/@datetime').extract_first()
            if len(time_list) == 25:
                date_time = time_list[:10]
                detail_time = time_list[11:19]
                pub_time = date_time + ' ' + detail_time
                if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
                    return
                response.meta['pub_time'] = pub_time
                response.meta['title'] = i.xpath('.//header[@class="entry-header"]/h2/a/text()').extract_first()
                response.meta['abstract'] = i.xpath('.//div[@class="entry-content clearfix"]/p/text()').extract_first()
                detail_url = i.xpath('.//span[@class="posted-on"]/a/@href').extract_first()
                yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)
        next_url = response.xpath('//li[@class="previous"]/a/@href').extract_first()
        if next_url is None:
            return
        yield Request(next_url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        p_lst = response.xpath('//div[@class="entry-content clearfix"]//p')
        body = ''
        for i in p_lst:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace('\n', '')
            body += p + '\n'
        body = self.clear_none(self.clear(body))
        if body != '':
            title = response.meta['title']
            abstract = response.meta['abstract']
            title, abstract, body = self.correct_news(title, abstract, body)
            images = []
            image = response.xpath('//div[@class="featured-image"]/a/img/@src').extract_first()
            if image is not None:
                images.append(image)
            images_tag = response.xpath(
                '//div[@class="entry-content clearfix"]//figure[@class="wp-caption aligncenter"]'
                )
            for tag in images_tag:
                image = tag.xpath('./img/@src').extract_first()
                if image is not None:
                    images.append(image)
            item['title'] = title
            item['abstract'] = abstract
            item['body'] = self.clear(body)
            item['pub_time'] = response.meta['pub_time']
            item['category1'] = response.meta['category1']
            item['images'] = images
            yield item
