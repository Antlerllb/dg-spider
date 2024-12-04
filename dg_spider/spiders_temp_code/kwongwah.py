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

import re

# author : 华上瑛
time_dict = {'Januari': '01', 'Februari': '02', 'Mac': '03', 'April': '04', 'Mei': '05', 'Jun': '06', 'Julai': '07',
             'Ogos': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Disember': '12', 'pm': 12,
             'am': 0}
drop_urls = ['http://epaper.kwongwah.com.my','https://www.upal.com.my/?ref=aMQiBRNch2','https://www.kwongwah.com.my/','https://www.kwongwah.com.my/?p=853685']

# auuthor:华上瑛
class KwongwahSpider(BaseSpider):
        name = 'kwongwah'
        website_id = 143
        language_id = 2266
        start_urls = ['http://www.kwongwah.com.my']  # http://www.kwongwah.com.my
        custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2", 'PROXY': "02"}

        def parse(self, response):  # 初始页面，解析列表和其他数据
            soup = BeautifulSoup(response.text, 'lxml')
            navigation = soup.select("ul.td-mobile-main-menu > li > a")
            for category in navigation:
                href = category.get('href')
                category1 = category.text
                if 'http' not in href:
                    href = 'https://www.kwongwah.com.my' + href
                if href not in drop_urls:
                    yield Request(url=href, callback=self.parse_page, meta={'category1':category1})

        def parse_page(self, response):
            soup = BeautifulSoup(response.text, 'lxml')
            articles = soup.select('div.td_module_2.td_module_wrap.td-animation-stack')

            flag = True
            if OldDateUtil.time is not None:
                time = articles[-1].select('div > span > time')[0].get('datetime')
                pub_time_ = time.split('+08')
                pub_time = " ".join(pub_time_)
                last_time = pub_time
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                for article in articles:
                    time1 = article.select('div > span > time')[0].get('datetime')
                    pub_time_1 = time1.split('+08')
                    pub_time1 = " ".join(pub_time_1)

                    href = article.select('div > div > a')[0].get('href')
                    title = article.select('div > div > a')[0].get('title')
                    img = [article.select('div > div > a > img')[0].get('src')]
                    yield Request(url=href, callback=self.parse_item, meta={'title':title,'images':img,'pub_time':pub_time1,'category1': response.meta['category1']})
            else:
                flag = False
                self.logger.info("时间截止")

            if flag:
                if response.url.split('/')[-1] == "" :
                    next_page = response.url+'page/2'
                    yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
                else:
                    try:
                        next_page_link = "/".join(response.url.split('/')[:-2]) + str(int(response.url.split('/')[-1])+1)
                        yield Request(url=next_page_link, callback=self.parse_page, meta=response.meta)
                    except:
                        self.logger.info("no more pages")

        def parse_item(self, response):  # 点进文章里面的内容
            soup = BeautifulSoup(response.text, 'lxml')
            body_list = soup.select('div.td-post-content > p')
            body = ""
            for b in body_list:
                body += b.text.replace('\n'," ").strip()

            abstract = body.split('。')[0].strip()

            item = NewsItem(language_id=self.language_id)
            item['title'] = response.meta['title']
            item['abstract'] = abstract  # response.meta['abstract']
            item['body'] = body  # response.mata['body']
            item['pub_time'] = response.meta['pub_time']
            item['category1'] = response.meta['category1']
            item['category2'] =""
            item['images'] = response.meta['images']

            yield item

