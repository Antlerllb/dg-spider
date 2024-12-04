# encoding: utf-8
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
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




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

#Author: 贺佳伊
# check：pys
# pass
class debkaSpiderSpider(BaseSpider):
    name = 'debka'
    website_id = 356
    language_id = 1866
    start_urls = ['http://debka.com']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        'Accept-Encoding': 'gzip, deflate, br'
    }
    proxy = "00"

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.headers)
    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        a = soup.select('#tag_cloud-5 > div > a')
        for i in a:
            response.meta['category1'] = i.text
            news_page_url =i.get('href')
            yield Request(url=news_page_url, callback=self.parse_page, meta=response.meta)
    def parse_page(self,response):
        time.sleep(0.5)
        soup=BeautifulSoup(response.text,'lxml')
        flag = True
        a = soup.select('#content > div > article ')
        for i in a:
            t = i.select_one(' div.article-content.clearfix > div.below-entry-meta > span.posted-on > a > time').get('datetime')
            pub_time = t[0:10] + ' ' + t[11:-6]
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
             for i in a:
                news_url = i.select_one('div.article-content.clearfix > header > h2 > a').get('href')
                response.meta['title'] = i.select_one(' div.article-content.clearfix > header > h2 > a').text
                t = i.select_one('div.article-content.clearfix > div.below-entry-meta > span.posted-on > a > time').get('datetime')
                response.meta['time'] = t[0:10] + ' ' + t[11:-6]
                try:
                    response.meta['abstract'] = i.select_one('div > p').text
                except:
                    response.meta['abstract'] = None
                try:
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
                except:
                        pass
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            try:
                next_page_url = soup.select_one('#content > ul > li.previous > a').get('href')
                yield Request(url=next_page_url, callback=self.parse_page,meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        a = soup.select('#content > div > article > div.article-content.clearfix > div.below-entry-meta > span.tag-links > a')
        if(len(a) > 1):
            item['category2'] = a[1].text
        else:
            item['category2'] = None
        item['images'] =[]
        item['abstract'] = response.meta['abstract']
        try:
            item['body'] = soup.select_one('#content > div > article > div.article-content.clearfix > div.entry-content.clearfix > div.pf-content > p').text
        except:
            item['body'] = None
        yield item