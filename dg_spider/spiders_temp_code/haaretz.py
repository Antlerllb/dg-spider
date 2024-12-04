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
month = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12',
}
Page = {
    'p': 1
}

#Author: 贺佳伊
# check: pys pass
class DemoSpiderSpider(BaseSpider):
    name = 'haaretz'
    website_id = 362
    language_id = 1866
    start_urls = ['https://www.haaretzdaily.com']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        }

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], headers=self.headers)

    def parse(self,response):
        time.sleep(5)
        soup=BeautifulSoup(response.text,'lxml')
        flag = True
        a = soup.select('#content_box > article')
        for i in a:
            t = i.select_one(' header > div > span.thetime.date.updated > span').text
            tt = t.split()
            pub_time = str(tt[2]) + '-' + str(month[tt[0]]) + '-' + str(tt[1][:-1]).rjust(2, '0') + ' 00:00:00'
        if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(pub_time):
             for i in a:
                response.meta['category1'] = i.select_one('#content_box > article > header > div > span.thecategory > a').text
                news_url = i.select_one(' header > h2 > a').get('href')
                response.meta['title'] = i.select_one(' header > h2 > a').text
                ab = i.select_one('div.front-view-content').text.split('.')
                response.meta['abstract'] = ab[0]
                t = i.select_one(' header > div > span.thetime.date.updated > span').text.split()
                response.meta['time'] = str(t[2]) + '-' + str(month[t[0]]) + '-' + str(t[1][:-1]).rjust(2, '0') + ' 00:00:00'
                try:
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
                except:
                    pass
        else:
            self.logger.info("时间截至")
            flag = False

        if flag:
            try:
                Page['p'] = Page['p'] + 1
                next_page_url = 'https://www.haaretzdaily.com/page/'+str(Page['p'])+'/'
                yield Request(url=next_page_url, callback=self.parse,meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup = BeautifulSoup(response.text,'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['abstract'] = response.meta['abstract']
        a1 = soup.select('#content_box > div > div.single_post > header > img')
        item['images'] = []
        for i in a1:
            item['images'].append(i.get('src'))
        item['body'] = ''
        a = soup.select('#content_box > div > div.single_post > div > div > p')
        for i in a:
            item['body'] += i.text + '\n\r'
        yield item