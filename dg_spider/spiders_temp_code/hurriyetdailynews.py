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

import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


# author : 梁智霖
class HurriyetdailynewsSpider(BaseSpider):
    name = 'hurriyetdailynews'
    website_id = 1829
    language_id = 1866
    allowed_domains = ['hurriyetdailynews.com']
    start_urls = ['https://hurriyetdailynews.com']
    # is_http = 1 若网站使用的是http协议，需要加上这个类成员(类变量)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('div.col-md-9.col-sm-10 > ul > li > a')[0:2] + soup.select(
            'div.col-md-9.col-sm-10 > ul > li > a')[3:6]
        for category1 in categories:
            category_url = 'https://hurriyetdailynews.com' + category1.get('href')
            yield Request(url=category_url, callback=self.parse_page, meta={'category1': category1.text})


    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        last_time = time.strftime("%Y-%m-%d %H:%M:%S")
        articles = soup.select('div.module.news-single-complete ') + soup.select('div >div.news') + soup.select('ol >li')
        for article in articles:
            article_url = 'https://hurriyetdailynews.com' + article.select_one('a').get('href')
            title = article.select_one('a > h3').text
            yield Request(url=article_url, callback=self.parse_item,
                          meta={'category1': response.meta['category1'], 'title': title})

        if OldDateUtil.time is not None:
            if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                yield scrapy.Request(url=article_url, callback=self.parse_page)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=article_url, callback=self.parse_page)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        body = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('div.content > p')
             if paragraph.text != '' and paragraph.text != ' '])
        item['body'] = body
        abstract = soup.select_one('div.content > p').text
        item['abstract'] = abstract
        images = 'https:' + [img.get('src') for img in soup.select('div.content > img')][0]
        item['images'] = images
        time = soup.select_one('ul.info > li').text.split()
        pub_time = "{}-{}-{}".format(time[2], str(OldDateUtil.EN_1866_DATE[time[0]]).zfill(2), time[1]) + ' ' + time[3]
        item['pub_time'] = pub_time
        yield item