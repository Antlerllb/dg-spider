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
year = ['2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015']     #大部分标签都只有2015年以后的，有的标签下只有2020年之后的内容

#Auther: 贺佳伊
# check: pys  pass
class DemoSpiderSpider(BaseSpider):
    name = 'newswalla'
    website_id = 1025
    language_id = 1926
    start_urls = ['https://news.walla.co.il/']

    def parse(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        a = soup.select(
            '#root > div > section.walla-core-container.css-11x5rb1.css-1w3f4nx > section.css-12flape.css-1pnkrju > main > div> a.css-h2ezfn')
        for t in year:          #不同年份
            for i in a:
                response.meta['category1'] = i.text
                news_page_url = i.get('href').replace('category', 'archive')+'?year=' + t  # 跳转到各标签页面
                try:
                    yield Request(url=news_page_url, callback=self.parse_year, meta=response.meta)
                except:
                    pass

    def parse_year(self, response):                 #每个月的文章，要跳转新的网页才能访问，然后不断翻页
        soup = BeautifulSoup(response.text,'lxml')
        s = soup.select(
            '#root > div > section.walla-core-container.css-11x5rb1.css-1nwbluu > section > main > section > div > div > a')
        for i in s:
            news_page_url = 'https://news.walla.co.il' + i.get('href')
            response.meta['page'] = 1
            response.meta['url'] = news_page_url
            yield Request(url=news_page_url, callback=self.parse_page, meta=response.meta)

    def parse_page(self,response):
        # time.sleep(3)
        soup=BeautifulSoup(response.text,'lxml')
        flag = True
        a = soup.select('#root > div > section.walla-core-container.css-11x5rb1.css-1nwbluu > section > main > section > div > ul > li ')
        for i in a:
            t = i.select_one('a > article > div > footer > div.pub-date').text
            if (len(t) == 24):                  #新闻发布日期的格式有的不同，要分类处理
                pub_time = t[20:24] + '-' + t[17:19] + '-' + t[14:16] + ' ' + t[8:13] + ':00'
            else:
                t0 = t.split('/')
                pub_time = t0[2] + '-' + t0[1].rjust(2, '0') + '-' + t0[0][6:].rjust(2, '0') + ' ' + t0[0][:5] + ':00'
        if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(pub_time):
             for i in a:
                news_url = i.select_one('a').get('href')
                response.meta['title'] = i.select_one('a > article > div > h3').text
                t = i.select_one('a > article > div > footer > div.pub-date').text
                if (len(t) == 24):
                    response.meta['time'] = t[20:24] + '-' + t[17:19] + '-' + t[14:16] + ' ' + t[8:13] + ':00'
                else:
                    t0 = t.split('/')
                    response.meta['time'] = t0[2] + '-' + t0[1].rjust(2, '0') + '-' + t0[0][6:].rjust(2, '0') + ' ' + t0[0][:5] + ':00'
                response.meta['abstract'] = i.select_one(' a > article > div > p').text
                try:
                    yield Request(url=news_url, callback=self.parse_item, meta=response.meta)
                except:
                    pass
        else:
            self.logger.info("时间截至")
            flag = False
        if flag:
            response.meta['page'] = response.meta['page'] + 1
            try:
                next_page_url = self.start_urls +'&page=' +str(response.meta['page'])
                yield Request(url=next_page_url, callback=self.parse_page,meta=response.meta)
            except:
                pass

    def parse_item(self, response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['time']
        item['body'] = soup.select_one('#root > div > section > section > section > main > div > article > section > section').text
        item['abstract'] = response.meta['abstract']
        item['images'] = []
        try:
            a = soup.select_one(
                '#root > div > section > section > section > main > div > article > section.item-main-content > section > section > div > figure >picture >img').get(
                'srcset')
            pics = a.split()
            for i in pics:
                if (i[0] == 'h'):
                    item['images'].append(i)
        except:
            pass
        yield item