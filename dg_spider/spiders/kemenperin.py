# -*- codeing = utf-8 -*-
# @Time : 2022/7/18 9:43
# @Author : 肖梓俊

# @software: PyCharm




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

month = {
        'Januari': '01',
        'Februari': '02',
        'März': '03',
        'April': '04',
        'Mai': '05',
        'Mei':'05',
        'Juni': '06',
        'Juli': '07',
        'August': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Desember': '12',
        'Maret':'03',
        'Agustus':'08'

    }

# author : 肖梓俊
# check:why
class RakyatmerdekaSpider(BaseSpider):
    name = 'kemenperin'
    website_id = 95
    language_id = 1901

    start_urls = ['https://kemenperin.go.id/index.php?&hal=1']

    def parse(self, response):
        # meta = response.meta
        # categories = response.xpath('//*[@id="head"]/div//li/a')
        # # print(categories)
        # for category in categories:
        #     # print(category)
        #     page_link = "https://kemenperin.go.id"+category.xpath('./@href').get()
        #     # print(page_link)
        #     category1 = category.xpath('./text()').get()
        #     meta['data'] = {
        #         'category1': 'category1'
        #     }
        #     yield Request(url=page_link, callback=self.parse_page, meta={'category1': 'category1'})
        soup = BeautifulSoup(response.text, 'lxml')

        if len(soup.select('.col-md-12 > ul > li'))>0:
            for i in soup.select('.col-md-12 > ul > li'):
                t = (i.select_one('h5').text.strip().split(' '))
                t[2], t[0] = t[0], t[2]
                t[1] = month[t[1]]
                t = ('-'.join(t) + " 00:00:00")

                title = (i.select_one('h3').text)
                abstract = (i.select_one('.text-cut').text)
                url = "https://kemenperin.go.id" + i.select_one('.read').get('href')
                meta = {
                    'title': title,
                    'time': t,
                    'abstract': abstract
                }
                yield Request(url=url, callback=self.parse_item, meta=meta)

            t = (soup.select_one('h5').text.strip().split(' '))
            t[2], t[0] = t[0], t[2]
            t[1] = month[t[1]]
            t = ('-'.join(t) + " 00:00:00")

            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(t) >= OldDateUtil.time:
                cur_page = int(response.url.split('=')[1])
                n_url = response.url.split('=')[0]
                yield Request(url=n_url+"="+str(cur_page+1))



    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = 'News'
        item['title'] = meta['title']
        item['pub_time'] = meta['time']

        item['body'] = '\n'.join([paragraph.strip() for paragraph in
                                  ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                                      '//div[@class="col-md-12 col-lg-12 col-xs-12 col-sm-12"]/p')] if
                                  paragraph.strip() != '' and paragraph.strip() != '\xa0' and paragraph.strip() is not None])

        item['abstract'] = item['body'].split('\n')[0]
        soup = BeautifulSoup(response.text, 'lxml')
        item['images'] = [img.get('src') for img in soup.select('.row img')]
        return item