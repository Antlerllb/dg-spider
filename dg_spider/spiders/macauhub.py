import scrapy
import requests

import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class MacauhubSpider(BaseSpider):  # 类名重命名
    author = '刘雨鑫'
    lan_num = 3
    name = 'macauhub'  # name的重命名
    website_id = 2149  # id一定要填对！
    language_id = 2122  # id一定要填对！
    start_urls = ['https://macauhub.com.mo/zh/category/news/', 'https://macauhub.com.mo/category/news/',
                  'https://macauhub.com.mo/pt/category/news/']

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
        url = response.request.url
        response.meta['url'] = url
        yield scrapy.Request(
            url + 'page/' + str(1) + '/', callback=self.parse_page, meta=response.meta
            )

    def parse_page(self, response):  # 新闻列表页，用于点进每个新闻
        block = response.xpath('//div[@class="main-sub-news-block"]')
        if len(block) == 0:  # 存在空页码
            return
        time_list = block[0].xpath('./div[2]/div/text()').extract_first()
        if response.meta['url'][24] == 'z':
            first_time = f'{time_list[0: 4]}-{time_list[5: 7]}-{time_list[8: 10]} 00:00:00'
        else:
            time_list = time_list.split(' ')
            first_time = f'{time_list[2]}-{str(OldDateUtil.EN_1866_DATE[time_list[1]]).zfill(2)}-{time_list[0]} 00:00:00'
        if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(
                first_time
                ) < OldDateUtil.time:  # OldDateUtil.time: 当前时间的3天前的时间戳
            return
        for i in block:  # 可补：页码越界判断
            time_list = i.xpath('./div[2]/div/text()').extract_first()
            if response.meta['url'][24] == 'z':
                pub_time = f'{time_list[0: 4]}-{time_list[5: 7]}-{time_list[8: 10]} 00:00:00'
            else:
                time_list = time_list.split(' ')
                pub_time = f'{time_list[2]}-{str(OldDateUtil.EN_1866_DATE[time_list[1]]).zfill(2)}-{time_list[0]} 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:  # 是三天前的新闻
                return
            response.meta['pub_time'] = pub_time
            a_list = i.xpath('./div[@class="mh-news-desc"]//text()').extract()
            abstract = ''
            for j in a_list:
                abstract += j
            response.meta['abstract'] = abstract
            detail_url = i.xpath('./div[1]/h2/a/@href').extract_first()
            yield scrapy.Request(
                detail_url, callback=self.parse_item, meta=response.meta
                )
        next_url = response.xpath('//div[@class="pagination"]//a[last()-1]/@href').extract_first()
        yield Request(next_url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):  # 爬取新闻信息
        item = NewsItem(language_id=self.language_id)
        title = response.xpath(
            '/html/body/div[3]/div/div/div[2]/div/div[2]/div/div[1]/div/h2/text()'
            ).extract_first()
        category1 = response.xpath(
            '/html/body/div[3]/div/div/div[2]/div/div[2]/div/div[1]/div/div[1]/div[2]/div/a[1]/text()'
            ).extract_first()
        item['images'] = response.xpath(
            '/html/body/div[3]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/img/@src'
            ).extract()
        body_list = response.xpath('//div[@class="detail-body-text"]//p')
        body = ''
        for i in body_list:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace(' ', '').replace('\n', '')
            body += p + '\n'
        body = self.clear_none(self.clear(body))
        if len(body.split('\n')) == 1 or body == '':
            body = title + '\n' + response.meta['abstract'] + '\n' + body
        item['title'] = title
        item['body'] = self.clear_none(self.clear(body))
        item['pub_time'] = response.meta['pub_time']
        item['abstract'] = response.meta['abstract']
        if response.meta['url'][24] == 'z':
            vb = '安哥拉'
            self.language_id = 1813
        elif response.meta['url'][24] == 'c':
            vb = 'Angola'
            self.language_id = 1866
        elif response.meta['url'][24] == 'p':
            vb = 'Angola'
            self.language_id = 2122
        if category1 is None:
            category1 = vb
        item['category1'] = category1
        yield item
