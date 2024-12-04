# encoding: utf-8
import scrapy
import requests
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
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



import re
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil as date

# author:凌敏
class rtpSpider(BaseSpider):
    name = 'rtp'
    website_id = 2074
    language_id = 2122
    start_urls = ['https://www.rtp.pt/noticias/rc/view/home-last-articles/homepage/1416359/1',
                  'https://www.rtp.pt/noticias/rc/view/home-last-articles/sports/1416356/1'
                  ]  # http://www.rtp.pt/
    # is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        article = soup.select('body > div')
        for i in article:
            title = i.find('a').find('div', class_='row').find('div', class_='col-7 col-md-8').find('h4').text
            if 'Edição' in title:  # 内容为视频
                continue
            else:
                content_url = i.find('a').get('href')
                images = i.find('a').find('div', class_='row').find('div', class_='col-5 col-md-4 pr-0 pr-sm-3').find('img').get('src')
                category1 = content_url.split('/')[4]
                meta1 = {'category1': category1,
                         'images': images,
                         'title': title}
                last_time = self.parse3(content_url)
                yield scrapy.Request(url=content_url, callback=self.parse2, meta=meta1)
        url = response.url.split('1416359/')[0]+'1416359/'+str(int(response.url.split('1416359/')[1])+1)
        if OldDateUtil.time is not None:
            if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                yield scrapy.Request(url, callback=self.parse)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url, callback=self.parse)

    def parse2(self, response, **kwargs):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, features='lxml')
        if soup.find('time', class_='timeago ct_pub') is not None:
            date = soup.find('time', class_='timeago ct_pub').get('datetime').split('T')[0]
            time = soup.find('time', class_='timeago ct_pub').get('datetime').split('T')[1].split('Z')[0]
            item['pub_time'] = date+' '+time
        else:
            date = soup.find('time', class_='timeago ct_mod').get('datetime').split('T')[0]
            time = soup.find('time', class_='timeago ct_mod').get('datetime').split('T')[1].split('Z')[0]
            item['pub_time'] = date + ' ' + time
        item['body'] = ''
        for i in soup.find_all('p', class_='article-lead'):
            item['body'] += i.text
        item['abstract'] = item['body'].split(',')[0]
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        item['title'] = response.meta['title']
        item['images'] = response.meta['images']
        yield item

    @staticmethod
    def parse3(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features='lxml')
        if soup.find('time', class_='timeago ct_pub') is not None:
            date = soup.find('time', class_='timeago ct_pub').get('datetime').split('T')[0]
            time = soup.find('time', class_='timeago ct_pub').get('datetime').split('T')[1].split('Z')[0]
            last_time = date+' '+time
        else:
            date = soup.find('time', class_='timeago ct_mod').get('datetime').split('T')[0]
            time = soup.find('time', class_='timeago ct_mod').get('datetime').split('T')[1].split('Z')[0]
            last_time = date + ' ' + time
        return last_time


