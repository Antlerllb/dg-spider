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


class LademaSpider(BaseSpider):
    name = "ladema"
    website_id = 1301
    language_id = 2181
    author = '刘雨鑫'
    i = 1
    lan_num = 1

    def start_requests(self):
        yield scrapy.Request('https://lademajagua.cu/', callback=self.parse)

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
        body = LademaSpider.clear_none(LademaSpider.clear(body))
        title = LademaSpider.clear_none(LademaSpider.clear(title))
        if abstract != '':
            abstract = LademaSpider.clear_none(LademaSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def parse(self, response):
        li_list = response.xpath('/html/body/div[1]/header/nav/nav/div/ul//li')
        li_list.pop(0)
        for li in li_list:
            class_url = li.xpath('./a/@href').extract_first()
            # print(class_url)
            yield scrapy.Request(class_url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        block = response.xpath(
            '/html/body/div[1]/div[2]/section/div/div[1]/div/header[@class="archive-header"]/following-sibling::div'
            )
        for i in block:
            judge_tag = i.xpath('./@id').extract_first()
            response.meta['category1'] = judge_tag
            detail_url = i.xpath('.//div[@id="container_title"]/a/@href').extract_first()
            response.meta['abstract'] = i.xpath('.//div[@id="container_texto"]//text()').extract_first()
            if judge_tag == 'principalsec':
                time_list = i.xpath('.//abbr[@class="published"]/@title').extract_first().replace(',', '').split(' ')
                if len(time_list) == 5:
                    pub_time = f'{time_list[3]}-{str(OldDateUtil.ES_2181_DATE[time_list[2].capitalize()]).zfill(2)}-{time_list[1].zfill(2)} {time_list[4].split(":")[0].zfill(2)}:{time_list[4].split(":")[1].zfill(2)}:00'
                    if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
                        return
                    response.meta['pub_time'] = pub_time
                else:
                    response.meta['pub_time'] = None
            if judge_tag == 'secundariasec':
                response.meta['pub_time'] = None
            yield scrapy.Request(detail_url, callback=self.parse_, meta=response.meta)

    def parse_(self, response):
        item = NewsItem(language_id=self.language_id)
        pub_time = response.meta['pub_time']
        if pub_time is None:
            time_list = response.xpath(
                '/html/body/div[1]/div[2]/div/div[1]/article/header/section/h6/abbr/abbr/@title'
                ).extract_first().replace(',', '').split(' ')
            pub_time = f'{time_list[3]}-{str(OldDateUtil.ES_2181_DATE[time_list[2].capitalize()]).zfill(2)}-{time_list[1].zfill(2)} {time_list[4].split(":")[0].zfill(2)}:{time_list[4].split(":")[1].zfill(2)}:00'
            if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
                return
        abstract = response.meta['abstract']
        category1 = response.meta['category1']
        title = response.xpath('/html/body/div[1]/div[2]/div/div[1]/article/header/h1/text()').extract_first()
        p_list = response.xpath('/html/body/div[1]/div[2]/div/div[1]/article/div//text()').extract()
        body = ''
        for p in p_list:
            if p != '':
                body += p + '\n'
        title, abstract, body = self.correct_news(title, abstract, body)
        images = []
        image_list = response.xpath('/html/body/div[1]/div[2]/div/div[1]/article/div//figure')
        for i in image_list:
            image = i.xpath('./img/@src').extract_first()
            if image is not None:
                images.append(image)
        item['title'] = title
        item['abstract'] = abstract
        item['body'] = self.clear(body)
        item['category1'] = category1
        item['images'] = images
        item['pub_time'] = pub_time
        yield item


