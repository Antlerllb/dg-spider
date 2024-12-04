# encoding: utf-8

from bs4 import BeautifulSoup
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


import re
import scrapy
import requests


# author: 华上瑛
class PmogovSpider(BaseSpider):
    name = 'pmogov'
    website_id = 388
    language_id = 2036
    start_urls = ['http://www.pmo.gov.my/speech/','https://www.pmo.gov.my/media-statement/']

    proxy = '02'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept - encoding': 'gzip, deflate, br',
        'cache - control': 'max - age = 0',
        'cookie': 'pll_language=en; _ga=GA1.3.1830848142.1657606015; _gid=GA1.3.801834590.1657606015; PHPSESSID=c632dcf99871aa54be9ec4beb41ab971; aiovg_rand_seed=4284361228',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec - fetch - user': '?1',
        'upgrade-insecure-requests': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36'
    }

    def start_requests(self):
        for i in self.start_urls:
            yield Request(url=i,callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        flag = True
        table = soup.select('div #posts-table-1 > tbody')[0]
        category1 = response.url.split('/')[-2]
        articles = table.select('tr')
        if OldDateUtil.time is not None:
            last_time = articles[-1].select('td')[-1].text
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                href = article.select('td > a')[0].get('href')
                title = article.select('td')[0].text
                time = article.select('td')[-1].text
                yield Request(url=href, callback=self.parse_item,meta={'pub_time': time, 'category1': category1, 'title': title})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            self.logger.info("no more articles")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        content = soup.select('div.entry-content')[0]
        try:
            img = [content.select('div > figure > img')[0].get('src')]
        except:
            img = []
        body_ = content.select("p")
        body = " "
        for b in body_:
            body += b.text

        abstract_ = content.find_all("p", style="text-align: center;")
        abstract = " "
        for a in abstract_:
            abstract_list = [aa.text.strip() for aa in a.select('strong')]
            abstract += " ".join(abstract_list)

        if abstract==" ":
            abstract = body.split('.')[0]

        item['category1'] = response.meta['category1']
        item['category2'] = ""
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = img
        item['body'] = body
        item['abstract'] = abstract
        yield item



