# encoding: utf-8



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy

#   Author:叶雨婷
class MdesSpider(BaseSpider):
    name = 'mdes'
    start_urls = ['https://www.mdes.go.th/news/']
    website_id = 1613
    language_id = 2208

    #拿几个含新闻内容的模块的html文件的
    def parse(self, response):
        list_pages = ["119", "3", "109", "8", "9", "120", "116", "115"]
        for item in list_pages:
            meta_part = {'e': item}
        yield Request(url=self.start_urls[0] + item, callback=self.get_page, meta=meta_part)



    # 按照日期边翻页边拿链接
    def get_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        t = soup.select(' .col.date-news')[-1].text.strip().split('/')
        last_time = str(int(t[2])-543) + "-" + str(t[1]) + "-" + str(t[0]) + " 00:00:00"
        # 泰国时间年份要"-543"
        meta = {'pub_time_': last_time}
        for i in soup.select(' .card-title-news a'):
            yield Request(url=i.get('href'), callback=self.parse_pages, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            try:
                yield Request(url=soup.select(' .pagination>li')[-1].select_one('a').get('href'),
                              callback=self.get_page, meta=deepcopy(meta))
            except AttributeError:
                pass
        else:
            self.logger.info("Time Stop")
        # try:
        #     yield Request(url=soup.select(' .pagination>li')[-1].select_one('a').get('href'),
        #                   callback=self.get_page, meta=deepcopy(meta))
        # except AttributeError:
        #     pass

    # 填表的
    # 不同语言的界面标签不一样
    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = soup.select_one(' .title-page').text.strip()
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = soup.select_one(' .carousel-item.active img').get('src')
        item['body'] = soup.select_one(' .col-12').text
        item['category1'] = "ข่าวสารประชาสัมพันธ์"
        item['abstract'] = " "
        item['category2'] = soup.select_one(' .nav-item.active').text
        yield item
