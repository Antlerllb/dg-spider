# -*- codeing = utf-8 -*-
# @Time : 2022/7/19 12:17
# @Author : 肖梓俊
# @File : pu.py
# @software: PyCharm







from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
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
class puSpider(BaseSpider):
    name = 'pu'
    website_id = 98
    language_id =1952
    start_urls = ['https://www.pu.go.id/berita/kanal']

    def parse(self, response):
        meta = response.meta
        soup =BeautifulSoup(response.text,'lxml')

        for i in soup.select('article.blog-post'):
            t = (i.select_one('.d-flex .post-date').text.strip().split(' '))
            t[2], t[0] = t[0], t[2]
            t[1] = month[t[1]]
            t = ('-'.join(t) + " 00:00:00")

            title = (i.select_one('h2').text)
            abstract = (i.select_one('a p').text)
            url =i.select_one('a').get('href')
            meta = {
                'title': title,
                'time': t,
                'abstract': abstract
            }

            yield Request(url=url, callback=self.parse_item, meta=meta)

        t = (soup.select_one('.d-flex .post-date').text.strip().split(' '))
        t[2], t[0] = t[0], t[2]
        t[1] = month[t[1]]
        t = ('-'.join(t) + " 00:00:00")

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(t) >= OldDateUtil.time:
            try:
                url=soup.select('.pagination .page-item')[-1].select_one('a').get('href')
                yield Request(url=url)
            except:
                pass

    # def parse_page(self, response):
    #     flag = True
    #     articles = response.xpath("/html/body/div/section[2]/div/div/div/article[2]")
    #     meta = response.meta
    #     if OldDateUtil.time is not None:
    #         t = articles[-1].xpath('.//span[@class="post-date text-color-primary mr-1 pr-2"]/text()').get().replace(',', '').split(" ")
    #         last_time = "{}-{}-{}".format(t[2], month[t[0]], t[1]) + ' 00:00:00'
    #     if OldDateUtil.time is None or OldDateUtil.formate_time2time_stamp(last_time) >= OldDateUtil.time:
    #         for article in articles:
    #             tt = article.xpath('.//span[@class="post-date text-color-primary mr-1 pr-2"]/text()').get().replace(',', '').split(' ')
    #             pub_time = "{}-{}-{}".format(tt[2], date.OldDateUtil.EN_1866_DATE[tt[0]], tt[1]) + ' 00:00:00'
    #             article_url ="https://www.pu.go.id"+ article.xpath('.//article/a/@href').get()
    #             title = article.xpath('./article/a/text()').get()
    #             meta['data']['pub_time'] = pub_time
    #             meta['data']['title'] = title
    #             yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
    #     else:
    #         flag = False
    #         self.logger.info("时间截止")
    #     # 翻页
    #     if flag:
    #         if response.xpath(
    #                 '//ul[@class="pagination"]/li').get() is None:
    #             self.logger.info("到达最后一页")
    #         else:
    #             next_page = "https://www.pu.go.id"+response.xpath(
    #                 '//ul[@class="pagination"]/li')[-1]
    #             next_page=next_page.xpath(".//a/@href")
    #             yield Request(url=next_page.get(), callback=self.parse_page, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = 'News'
        item['category2'] = None
        item['title'] = meta['title']
        item['pub_time'] = meta['time']
        item['body'] = '\n'.join([paragraph.strip() for paragraph in
                                  ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                                      '//article/p')] if
                                  paragraph.strip() != '' and paragraph.strip() != '\xa0' and paragraph.strip() is not None])

        item['abstract'] = item['body'].split('\n')[0]
        soup = BeautifulSoup(response.text, 'lxml')
        item['images'] = [img.get('src') for img in soup.select('article img')]
        return item