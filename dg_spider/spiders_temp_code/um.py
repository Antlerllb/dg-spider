# encoding: utf-8
import html

import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.utils import spider




from scrapy.http.request import Request
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
import re

month_en = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

month_pt = {
    'Jan': '01',
    'Fev': '02',
    'Mar': '03',
    'Abr': '04',
    'Mai': '05',
    'Jun': '06',
    'Jul': '07',
    'Ago': '08',
    'Set': '09',
    'Out': '10',
    'Nov': '11',
    'Dez': '12'
}


# author : 张鸿兴
class UmSpider(BaseSpider):  # 类名重命名
    name = 'um'  # name的重命名
    language_id = 2122
    website_id = 2144  # id一定要填对！
    number = 450
    start_urls = ['https://www.um.edu.mo/pt-pt/category/news-and-press-releases/',
                  'https://www.um.edu.mo/zh-hant/category/news-and-press-releases/',
                  'https://www.um.edu.mo/category/news-and-press-releases/']
    url1 = 'https://www.um.edu.mo/'
    url2 = '/?category_name=news-and-press-releases'

    def parse(self, response):
        url = response.request.url
        if "pt-pt" in url:
            language_id = 2122
            lan = 'pt-pt/'
        elif "zh-hant" in url:
            language_id = 1813
            lan = 'zh-hant/'
        else:
            language_id = 1866
            lan = ''
        response.meta['lan_id'] = language_id
        response.meta['lan'] = lan
        soup = BeautifulSoup(response.text, 'html.parser')
        year = int(soup.select_one(
            'h1.um-archive__postyear').text)
        month = len(soup.select('div.um-archive__monthlist > '
                                'div.um-archive__mobiledropdown-content > ul > li'))
        start_url = self.url1 + lan + str(year) + '/' + str(month) + self.url2
        response.meta['year'] = year
        response.meta['month'] = month
        yield scrapy.Request(url=start_url, callback=self.parse_pages, meta=response.meta)

    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('article')
        item = NewsItem(language_id=self.language_id)
        for i in block:
            response.meta['title'] = i.select_one('h3').text
            href = i.select_one('a')['href']
            response.meta['category1'] = i.select_one('div.archive__postcat').text.strip()
            time_list = re.sub(r'\t', '', i.select_one('div.archive__postdate').text.strip())
            time_list = re.sub('\n+', '\n', time_list)
            # print(time_list)
            # print(response.meta['lan'])
            if response.meta['lan_id'] == 2122:
                time_list = re.sub('\n', ' ', time_list)
                time_list = time_list.split(' ')
                response.meta['pub_time'] = f'{time_list[2]}-{month_pt[time_list[1]]}-{time_list[0].zfill(2)} 00:00:00'
            elif response.meta['lan_id'] == 1813:
                time_list = re.split(r'年|月|日', time_list)
                response.meta['pub_time'] = f'{time_list[0]}-{time_list[1].zfill(2)}-{time_list[2].zfill(2)} 00:00:00'
            elif response.meta['lan_id'] == 1866:
                time_list = re.sub('\n', '', time_list)
                time_list = time_list.split(' ')
                response.meta['pub_time'] = f'{time_list[2]}-{month_en[time_list[1]]}-{time_list[0].zfill(2)} 00:00:00'
            # print(time_list)
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(
                    response.meta['pub_time']) >= OldDateUtil.time:  # 判断是否是最新的新闻
                yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)
        response.meta['month'] -= 1
        if response.meta['month'] == 0:
            response.meta['month'] = 12
            response.meta['year'] -= 1
        url = self.url1 + response.meta['lan'] + str(response.meta['year']) + '/' + str(
            response.meta['month']) + self.url2
        # print(url)
        yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)

    def parse_items(self, response):  # 主页，用于点进每个菜单
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        body = ''
        # print(soup.select_one('div.col-sm-8').select('p'))
        for i in soup.select_one('div.col-sm-8').select('p'):
            body += i.text.replace('\n', '')
            body += '\n'
        for i in soup.select_one('div.col-sm-8').select('tr'):
            body += i.text.strip() + '\n'
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['pub_time'] = response.meta['pub_time']
        if len(body) <= 10:
            body = ''
            for i in soup.select_one('div.col-sm-8').select('div'):
                body += i.text.replace('\n', '')
                body += '\n'
        if len(body) <= 10:
            body = soup.select_one('div.col-sm-8').text.replace('\n', '')
        item['body'] = re.sub('\n+', '\n', body).strip()
        # print(item['body'])
        item['abstract'] = item['body'].split('\n')[0]
        item['language_id'] = response.meta['lan_id']
        img_list = soup.select('#newsgallery > a')
        img = []
        for i in img_list:
            if i['href'] != "":
                img.append(i['href'])
        item['images'] = img
        # print(img)
        # print(item)
        yield item
