


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import zhconv


class IogovmoSpider(BaseSpider):  # 类名重命名
    author = '刘雨鑫'
    name = 'iogovmo'  # name的重命名
    lan_num = 2
    website_id = 2146  # 网站id
    language_id = 2122  # 语言id
    start_urls = ['https://www.io.gov.mo/cn/bo/', 'https://www.io.gov.mo/pt/bo/']
    year_max_cn = 0
    year_min_cn = 0
    year_cn = 0
    year_max_pt = 0
    year_min_pt = 0
    year_pt = 0
    url_cn = 'https://www.io.gov.mo/cn/bo/year/'
    url_pt = 'https://www.io.gov.mo/pt/bo/year/'

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

    def parse(self, response):  # 主页，用于点进每个菜单
        judge = response.xpath('//*[@id="content"]/div/div[1]/div/ol/li[1]/a/@href').extract_first()
        if 'cn' in judge:
            self.year_max_cn = response.xpath('//*[@id="ctrlName"]/option[1]/text()').extract_first()
            self.year_min_cn = response.xpath('//*[@id="ctrlName"]//option[last()]/text()').extract_first()
            self.year_cn = int(self.year_max_cn)
            current = self.url_cn
            class_url = self.url_cn + self.year_max_cn
        elif 'pt' in judge:
            self.year_max_pt = response.xpath('//*[@id="ctrlName"]/option[1]/text()').extract_first()
            self.year_min_pt = response.xpath('//*[@id="ctrlName"]//option[last()]/text()').extract_first()
            self.year_pt = int(self.year_max_pt)
            current = self.url_pt
            class_url = self.url_pt + self.year_max_pt
        yield scrapy.Request(
            class_url, callback=self.parse_page,
            meta={'current': current, 'judge': judge}
            )

    def parse_page(self, response):
        block = response.xpath('//table[@class="table table-striped"]//tr')
        time_list = block[1].xpath('./td/text()').extract()[2].replace('  ', '').split('\n')[1].split('/')
        first_time = f'{time_list[0]}-{time_list[1]}-{time_list[2][:2]} 12:00:00'
        if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(first_time) < OldDateUtil.time:
            return
        for i in block:
            time_list = i.xpath('./td/text()').extract()
            if len(time_list) == 0:
                continue
            time_list = time_list[-1].replace(' ', '').split('\n')[1].split('/')
            pub_time = f'{time_list[0]}-{time_list[1]}-{time_list[2][:2]} 12:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            response.meta['pub_time'] = pub_time
            response.meta['title'] = i.xpath('./td/a/text()').extract_first()
            url = i.xpath('./td/a/@href').extract_first()
            if url is not None:
                yield Request(url, callback=self.parse_item, meta=response.meta)
        if 'cn' in response.meta['judge']:
            if self.year_cn == int(self.year_min_cn):
                return
            self.year_cn -= 1
            yield scrapy.Request(
                response.meta['current'] + str(self.year_cn), callback=self.parse_page, meta=response.meta
                )
        elif 'pt' in response.meta['judge']:
            if self.year_pt == int(self.year_min_pt):
                return
            self.year_pt -= 1
            yield scrapy.Request(
                response.meta['current'] + str(self.year_pt), callback=self.parse_page, meta=response.meta
                )

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.meta['title']
        item['title'] = zhconv.convert(title, 'zh-hans')
        item['pub_time'] = response.meta['pub_time']
        item['images'] = []  # 该网站无图片
        body = ''
        p = ''
        block = response.xpath('/html/body/div[1]//ul//text()').extract()
        for i in block:
            body += i
        for i in body.split('\r'):
            p += i
        body = p.replace('\t', '')
        if body == '':
            body = title
        body = self.clear_none(self.clear(body))
        if len(body.split('\n')) == 1:
            body += body + '\n' + title
        if 'cn' in response.meta['judge']:
            self.language_id = 1813
            body = zhconv.convert(body, 'zh-hans')
            if len(body.split('\n')) == 0:
                item['abstract'] = zhconv.convert(title, 'zh-hans')
            else:
                item['abstract'] = self.clear(body.split('。')[0])
            item['category1'] = zhconv.convert('《公報》', 'zh-hans')
        elif 'pt' in response.meta['judge']:
            self.language_id = 2122
            if len(body.split('\n')) == 0:
                item['abstract'] = title
            else:
                item['abstract'] = self.clear(body.split(',')[0])
            item['category1'] = 'Boletim Oficial'
        item['body'] = body
        yield item
