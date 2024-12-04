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

import re

# author : 华上瑛



def convert_time(time_text):
    return time_text.split('+08:00')[0].replace('T'," ") # %Y-%m-%d %H:%M:%S


class MofgovSpider(BaseSpider):
    name = 'mofgov'
    website_id = 389
    language_id = 2036
    start_urls = ['https://www.mof.gov.my/portal/ms/arkib3/siaran-media','https://www.mof.gov.my/portal/ms/arkib3/ucapan',
                  'https://www.mof.gov.my/portal/ms/arkib3/akhbar'] #http://www.utusan.com.my/
    proxy = '02'

    def start_requests(self):
        for i in self.start_urls:
            yield Request(url=i, callback=self.parse_page)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div #archive-items')
        if OldDateUtil.time is not None:
            last_time = convert_time(articles[-1].select('div > dl > dd > div > time')[0].get('datetime'))

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                pub_time = convert_time(article.select('div > dl > dd > div > time')[0].get('datetime'))
                category1 = re.split(r'[?/]', response.url)[6]  # %Y-%m-%d %H:%M:%S

                href = 'https://www.mof.gov.my' + article.select('div > div > h2 > a')[0].get('href')
                title = article.select('div > div > h2 > a')[0].text.strip()
                try:
                    abstract = article.select('div > p > strong')[0].text
                except:
                    yield Request(url=href, callback=self.parse_item, meta={'pub_time':pub_time,'category1':category1,'title':title})
                else:
                    yield Request(url=href, callback=self.parse_item, meta={'pub_time':pub_time,'category1':category1,'title':title,'abstract':abstract})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            try:
                next_page = soup.select('ul.pagination > li')[-1].select('a')[0].get('href')
                next_page_link = 'https://www.mof.gov.my' + next_page
                yield Request(url=next_page_link, callback=self.parse_page, meta=response.meta)

            except:
                self.logger.info("no more pages")


    def parse_item(self, response):#点进文章里面的内容
        soup = BeautifulSoup(response.text, 'lxml')
        article = soup.find_all("div", itemprop="articleBody")[0].select('p')
        body = " "
        for b in article:
            body += b.text.strip()


        try:
            img = ['https://www.mof.gov.my' + soup.select('div.article-full-image > img')[0].get('src')]
        except:
            img = []

        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['body'] = body # response.mata['body']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['images'] = img  # response.meta['category2']
        try:
            item['abstract'] = response.meta['abstract']
        except:
            item['abstract'] = body.split('.')[0]

        yield item
