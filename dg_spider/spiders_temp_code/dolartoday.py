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
Spanish_simple_MONTH = {'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
                        'Ago': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12'}

DAY = {'1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06', '7': '07', '8': '08', '9': '09'}

class dolartodaySpider(BaseSpider):
    name = 'dolartoday'
    website_id = 1324
    language_id = 2181
    start_urls = ['https://dolartoday.com/category/noticias/']  # https://dolartoday.com
    # proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        last_time = ''
        for i in soup.select('#content > div')[1:-2]:
            images = i.find('div', class_='post-image').find('a').find('img').get('src')
            title = i.find('div', class_='post-title').find('h2').find('a').get('title')
            content_url = 'https://dolartoday.com'+i.find('div', class_='post-title').find('h2').find('a').get('href')
            time = i.find('div', class_='post-title').find('p', class_='meta').find('span', class_='meta-date').text
            year = time.split(' ')[3]
            month = Spanish_simple_MONTH[time.split(' ')[1]]
            day = time.split(' ')[2].split(',')[0]
            if int(day) < 10:
                day = DAY[day]
            pub_time = year+'-'+month+'-'+day+' 00:00:00'
            last_time = pub_time
            abstract = i.select('p')[-1].text
            category1 = response.url.split('/')[4]
            meta = {'title': title, 'images': images, 'abstract': abstract,
                    'pub_time': pub_time, 'category1': category1}
            yield scrapy.Request(url=content_url, callback=self.parse2, meta=meta)
        turn_page = 'https://dolartoday.com'+soup.find('div', class_='pagination clearfix').find('div', class_='left').find_all('a')[-2].get('href')
        if OldDateUtil.time is not None:
            if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_time):
                yield scrapy.Request(url=turn_page, callback=self.parse)
            else:
                self.logger.info("时间截止")
        else:
            yield scrapy.Request(url=turn_page, callback=self.parse)

    def parse2(self, response, **kwargs):
        item = NewsItem(language_id=self.language_id)
        item['body'] = ''
        soup = BeautifulSoup(response.text, features='lxml')
        for i in soup.select('#content > div > p')[1:]:
            item['body'] += i.text
        item['abstract'] = response.meta['abstract']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        item['category1'] = response.meta['category1']
        item['category2'] = ''
        yield item


