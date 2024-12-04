


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class NewsunSpider(BaseSpider):  # 类名重命名
    author = '刘雨鑫'
    name = 'newsun'  # name,字符长度不小于5位
    website_id = 2067
    language_id = 2122
    lan_num = 3
    topic_names = ['peace-and-security', 'economic-development', 'humanitarian-aid', 'climate-change', 'human-rights',
                   'un-affairs', 'women', 'law-and-crime-prevention', 'health', 'culture-and-education', 'sdgs',
                   'migrants-and-refugees']
    head_urls = ['https://news.un.org/pt/', 'https://news.un.org/en/', 'https://news.un.org/zh/']
    start_urls = ['https://news.un.org/zh/']

    @staticmethod
    def check_images(images):
        lst = []
        for i in images:
            if not i.startswith('http'):
                i = 'https://news.un.org/' + i
            lst.append(i)
        return lst

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
        for topic in self.topic_names:
            for head in self.head_urls:
                class_url = head + 'news/topic/' + topic
                yield scrapy.Request(class_url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):  # 翻页，符合条件进入下一页
        block = response.xpath(
            '/html/body/div[1]/div/div/div[4]/div/div/main/section/div[4]/div/div/div/div//div[@class="views-row"]'
            )
        for i in block:  # 可补：页码越界判断
            time_list = i.xpath('.//time[@class="datetime"]/@datetime').extract_first()
            if time_list is not None:
                pub_time = f'{time_list[0:4]}-{time_list[5:7]}-{time_list[8:10]} 12:00:00'
                if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(  # 判断当前新闻时间是否是三天前
                        pub_time
                        ):
                    return
                response.meta['category1'] = response.request.url.split('/')[6]
                response.meta['pub_time'] = pub_time
                response.meta['title'] = i.xpath(
                    './/span[@class="field field--name-title field--type-string field--label-hidden"]//text()'
                    ).extract_first()
                detail_url = 'https://news.un.org/' + i.xpath('.//a[@rel="bookmark"]/@href').extract_first()
                yield scrapy.Request(
                    detail_url,
                    callback=self.parse_item, meta=response.meta
                    )
        next_url = response.xpath('//a[@rel="next"]/@href').extract()  # 获取下一页的url
        if len(next_url) != 0:
            yield scrapy.Request(
                response.request.url.split('?')[0] + next_url[0], callback=self.parse_page, meta=response.meta
                )  # 进入下一页

    def parse_item(self, response):  # 爬取新闻信息
        item = NewsItem(language_id=self.language_id)
        body = ''
        tag = response.xpath(
            '/html/body/div[1]/div[1]/div/div[4]/div/div/main/section/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[@class="clearfix text-formatted field field--name-field-text-column field--type-text-long field--label-hidden field__item"]//p | //div[@class="clearfix text-formatted field field--name-field-text-column field--type-text-long field--label-hidden field__item"]//h4 | //div[@class="clearfix text-formatted field field--name-body field--type-text-with-summary field--label-hidden field__item"]//p'
            )
        if len(tag) != 0:
            for i in tag:
                p = ''
                for j in i.xpath('.//text()').extract():
                    p += j.replace('\xa0', '')
                body += p + '\n'
            body = self.clear_none(self.clear(body))
            abstract_list = response.xpath(
                '//div[@class="field-content"]/p//text() | //div[@class="views-field views-field-field-news-story-lead"]/div//text()'
                ).extract()
            if len(abstract_list) != 0:
                abstract = ''
                for i in abstract_list:
                    abstract += i
                item['abstract'] = abstract.replace('\n', '')
            elif len(abstract_list) == 0:
                abstract = body.split('\n')[0]
                item['abstract'] = abstract
            body = self.clear(body)
            if body == '' or len(body.split('\n')) == 1:
                body = response.meta['title'] + '\n' + item['abstract']
            body = self.clear_none(self.clear(body))
            images = []
            images_main = response.xpath('//div[@class="media-image"]//img/@src').extract_first()
            if images_main is not None:
                images.append(images_main)
            images_sub = response.xpath(
                '//div[@class="field field--name-thumbnail field--type-image field--label-hidden field__item"]//img/@src'
                ).extract()
            for i in images_sub:
                if i != 'null':
                    images.append(i)
            images_other = response.xpath('//img[@class="img-responsive"]/@src').extract()
            for i in images_other:
                if i != 'null':
                    images.append(i)
            images = self.check_images(images)
            item['images'] = images
            item['body'] = body
            item['category1'] = response.meta['category1']
            item['title'] = self.clear_none(response.meta['title'])
            item['pub_time'] = response.meta['pub_time']
            if 'zh' in response.request.url:
                self.language_id = 1813
            elif 'en' in response.request.url:
                self.language_id = 1866
            elif 'pt' in response.request.url:
                self.language_id = 2122
            yield item
