

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class LinternauteSpider(BaseSpider):
    name = 'linternaute'
    author = '潘宇豪'
    website_id = 2765
    language_id = 1884
    start_urls = ['https://www.linternaute.com']
    start = False
    this_year = ''
    this_month = ''

    @staticmethod
    def get_this_month():
        year = str(time.localtime().tm_year)
        month = str(time.localtime().tm_mon)
        LinternauteSpider.this_year = year
        LinternauteSpider.this_month = month
        return 'https://www.linternaute.com/actualite/list/' + year + '-' + month + '-1/'

    @staticmethod
    def get_last_month():
        if LinternauteSpider.this_month == '1':
            LinternauteSpider.this_month = '12'
            LinternauteSpider.this_year = str(int(LinternauteSpider.this_year) - 1)
        else:
            LinternauteSpider.this_month = str(int(LinternauteSpider.this_month) - 1)
        return 'https://www.linternaute.com/actualite/list/' + \
            LinternauteSpider.this_year + '-' + LinternauteSpider.this_month + '-1/'

    @staticmethod
    def time_fix(time):
        add_hour = int(time.split('+')[1].split(':')[0])
        date = time.split('T')[0] + ' ' + time.split('T')[1].split('+')[0]
        add_num = (8 - add_hour) * 3600
        return OldDateUtil.timestamp_to_datetime_str(OldDateUtil.str_datetime_to_timestamp(date) + add_num)

    def parse(self, response):
        if self.start:
            daily_uls = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/section/ul')
            daily_divs = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/section/div')
            del daily_uls[0]
            for i in range(len(daily_divs)):
                today = daily_divs[i].xpath('./div/text()').extract_first().split(' ')[0]
                today_date = LinternauteSpider.this_year + '-' + (LinternauteSpider.this_month
                                                                  if len(LinternauteSpider.this_month) == 2
                                                                  else '0' + LinternauteSpider.this_month) \
                             + '-' + (today if len(today) == 2 else '0' + today) + ' 00:00:00'
                if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(today_date):
                    li_lists = daily_uls[i].xpath('./li')
                    for li in li_lists:
                        detailed_url = li.xpath('./h4/a/@href').extract_first()
                        # print(detailed_url)
                        # 这里有一个id，也许会用到
                        title = li.xpath('./div/div/a/@title').extract_first()
                        images_pre = li.xpath('./div/div/a/@style')
                        if not images_pre:
                            continue
                        images = images_pre.extract_first().split('(')[1].strip(')')
                        abstract = li.xpath('./div/div/p/text()').extract_first()
                        # print(title)
                        # print(images)
                        # print(abstract)
                        response.meta['title'] = title
                        response.meta['images'] = [images]
                        response.meta['abstract'] = abstract
                        yield scrapy.Request(url=detailed_url, callback=self.parse_detailed, meta=response.meta)
                else:
                    return
            yield scrapy.Request(url=self.get_last_month(), callback=self.parse)
        else:
            self.start = True
            yield scrapy.Request(url=self.get_this_month(), callback=self.parse)

    def parse_detailed(self, response):
        category_pre = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/nav/div[3]/a/span/text()')
        if not category_pre:
            return
        category1 = category_pre.extract_first()
        # print(category1)
        pub_time_pre = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/article/div/aside[1]\
        /div/div/div[2]/dl/dt/time/@datetime').extract_first()
        if not pub_time_pre:
            return
        pub_time = self.time_fix(pub_time_pre)
        # print(pub_time)
        body = ''
        body_parts_num = 0
        body_parts = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/article/div/div/p')
        for body_part in body_parts:
            body_part_pre = body_part.xpath('./text()')
            if not body_part_pre:
                return
            body += body_part_pre.extract_first().replace('\n', '').replace('  ', '')
            body_parts_num += 1
            body += '\n'
        if body_parts_num == 0:
            return
        elif body_parts_num == 1:
            body = response.meta['abstract'] + '\n' + body
        # print(body)

        item = NewsItem(language_id=self.language_id)
        item['category1'] = category1
        item['pub_time'] = pub_time
        item['body'] = body
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['images'] = response.meta['images']
        yield item

