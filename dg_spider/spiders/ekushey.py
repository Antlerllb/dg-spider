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


class EkusheySpider(BaseSpider):
    name = 'ekushey'
    author = '刘雨鑫'
    website_id = 2283
    language_id = 1779
    lan_num = 1
    start_urls = ['https://www.ekushey-tv.com']

    @staticmethod
    def translate(time_list):
        lst = time_list
        detail_time = ''
        day = ''
        month = ''
        year = ''
        for i in lst:
            if i == lst[2]:
                month = str(OldDateUtil.BN_1779_DATE[i.replace(',', '')])
            elif i == lst[1]:
                for j in i:
                    if j != ':':
                        n = str(OldDateUtil.BN_1779_DATE[j])
                        day += n
            elif i == lst[3]:
                for j in i:
                    if j != ':':
                        n = str(OldDateUtil.BN_1779_DATE[j])
                        year += n
            else:
                for j in i.split(':'):
                    p = ''
                    for k in j:
                        p += str(OldDateUtil.BN_1779_DATE[k])
                    detail_time += p + ':'
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
        body = EkusheySpider.clear_none(EkusheySpider.clear(body))
        body = EkusheySpider.clear(body)
        title = EkusheySpider.clear_none(EkusheySpider.clear(title))
        if abstract != '':
            abstract = EkusheySpider.clear_none(EkusheySpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def parse(self, response):
        li_list = response.xpath('/html/body/header/div[2]/div/div/div/nav/div/div[2]/ul//li')
        for li in li_list:
            url = li.xpath('./a/@href').extract_first()
            response.meta['category1'] = li.xpath('./a/text()').extract_first()
            yield scrapy.Request(url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        block = response.xpath('//div[@class="DCatMorContain"]//div[@class="col-sm-6"]')
        if len(block) == 0:
            block = response.xpath('//div[@class="col-sm-12"]//div[@class="DCategoryListNews MarginTop20 something2"]')
        if len(block) != 0:
            for i in block:
                time_list = i.xpath('.//p[@class="DCatDate"]/text()').extract()
                if len(time_list) != 0:
                    pub_time = self.translate(time_list[0].split(' '))
                else:
                    time_list = i.xpath('.//p[@class="pDate"]/text()').extract_first()
                    time_list = time_list.split(' ')
                    time_list.pop(1)
                    time_list.pop(-1)
                    pub_time = self.translate(time_list)
                if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
                    return
                response.meta['pub_time'] = pub_time
                images = i.xpath('.//img')
                img_list = []
                for j in images:
                    image = j.xpath('./@src').extract_first()
                    if image is not None:
                        img_list.append(image)
                response.meta['images'] = img_list
                detail_url = i.xpath('./div/a/@href').extract_first()
                if detail_url is None:
                    detail_url = i.xpath('.//div[@class="col-sm-8"]/a/@href').extract_first()
                yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)
        next_url = response.xpath('//ul[@class="pagination"]//li[last()-1]/a/@href').extract_first()
        if next_url != '#' and next_url is not None:
            yield scrapy.Request(next_url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        category1 = response.meta['category1']
        pub_time = response.meta['pub_time']
        images = response.meta['images']
        title = response.xpath('/html/body/div[2]/main/div/div[1]/div[3]/div/div[1]/h1/text()').extract_first()
        if title is not None:
            abstract = response.xpath(
                '//div[@class="col-sm-12 DDetailsBody MarginTop10"]/p[1]//text()'
                ).extract_first()
            p_list = response.xpath('//div[@class="col-sm-12 DDetailsBody MarginTop10"]//p')
            body = ''
            for i in p_list:
                p = ''
                for j in i.xpath('.//text()').extract():
                    p += j.replace('\n', '')
                body += p + '\n'
            title, abstract, body = self.correct_news(title, abstract, self.clear(body))
            item['title'] = title
            item['abstract'] = abstract
            item['body'] = body
            item['category1'] = category1
            item['images'] = images
            item['pub_time'] = pub_time
            yield item
        else:
            pass



