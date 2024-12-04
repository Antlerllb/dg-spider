# encoding: utf-8
from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


from scrapy.utils import spider
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
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
import html
import re


# author : 张鸿兴
class UmeduSpider(BaseSpider):  # 类名重命名
    author = "张鸿兴"
    name = 'umedu'  # name的重命名
    language_id = 2122
    website_id = 2191  # id一定要填对！
    # start_urls = ['https://www.um.edu.mo/pt-pt/category/news-and-press-releases/', # 网站葡语文章少，英语文章多
    start_urls = ['https://www.um.edu.mo/zh-hant/category/news-and-press-releases/',
                  'https://www.um.edu.mo/category/news-and-press-releases/']
    url1 = 'https://www.um.edu.mo/'
    url2 = '/?category_name=news-and-press-releases'
    month_pt = OldDateUtil.PT_2122_DATE
    month_en = OldDateUtil.EN_1866_DATE

    # print(1)
    @staticmethod
    def formalize(category, title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ').replace('\n', '')
        title = re.sub(' +', ' ', title).strip().strip('\n')
        body = re.sub('<br>.*?<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub(' +', ' ', body).strip()
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        if language_id == 1813:
            category, title, abstract, body = convert(category, 'zh-cn'), convert(title, 'zh-cn'), \
                                              convert(abstract, 'zh-cn'), convert(body, 'zh-cn'),
        return category, title, abstract, body

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
        # start_url = 'https://www.um.edu.mo/zh-hant/2023/6/?category_name=news-and-press-releases/presss-release/'
        # print(start_url)
        yield scrapy.Request(url=start_url, callback=self.parse_pages, meta=response.meta)

    cnt = 0

    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('article')
        # print(block)
        for i in block:
            href = i.select_one('a')['href']
            # href = 'https://www.um.edu.mo/zh-hant/news-and-press-releases/presss-release/detail/55861/'
            # print(href)
            time_list = re.sub(r'\t', '', i.select_one('div.archive__postdate').text.strip())
            time_list = re.sub('\n+', '\n', time_list)
            # print(time_list)
            # print(response.meta['lan'])
            if response.meta['lan_id'] == 2122:
                time_list = re.sub('\n', ' ', time_list)
                time_list = time_list.split(' ')
                response.meta[
                    'pub_time'] = f'{time_list[2]}-{str(self.month_pt[time_list[1]]).zfill(2)}-{time_list[0].zfill(2)} 00:00:00'
            elif response.meta['lan_id'] == 1813:
                time_list = re.split(r'年|月|日', time_list)
                # print(time_list)
                response.meta[
                    'pub_time'] = f'{time_list[0]}-{time_list[1].zfill(2)}-{time_list[2].zfill(2)} 00:00:00'
            elif response.meta['lan_id'] == 1866:
                time_list = re.sub('\n', '', time_list)
                time_list = time_list.split(' ')
                response.meta[
                    'pub_time'] = f'{time_list[2]}-{str(self.month_en[time_list[1]]).zfill(2)}-{time_list[0].zfill(2)} 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(
                    response.meta['pub_time']) < OldDateUtil.time:  # 判断是否是最新的新闻
                return
            # href = "https://www.um.edu.mo/news-and-press-releases/press-release/detail/38470/"
            response.meta['category1'] = i.select_one('div.archive__postcat').text.strip()
            response.meta['title'] = i.select_one('h3').text
            # print(href)
            # print(response.meta['title'])
            self.cnt += 1
            yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)
        response.meta['month'] -= 1
        if response.meta['month'] == 0:
            response.meta['month'] = 12
            response.meta['year'] -= 1
        url = self.url1 + response.meta['lan'] + str(response.meta['year']) + '/' + str(
            response.meta['month']) + self.url2
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
        title = response.meta['title']
        item['category1'] = response.meta['category1']
        item['pub_time'] = response.meta['pub_time']
        if len(body) <= 5:
            body = ''
            for i in soup.select_one('div.col-sm-8').select('div'):
                body += i.text.replace('\n', '')
                body += '\n'
        body = body.strip()
        if len(body) <= 7:
            body = soup.select_one('div.col-sm-8').text.replace('\n', '')
        body = body.strip()
        # print(body)
        abstract = None
        # print(abstract)
        item['language_id'] = response.meta['lan_id']
        # print(abstract)
        img_list = soup.select('#newsgallery > a')
        img = []
        for i in img_list:
            if i['href'] != "":
                img.append(i['href'])
        item['images'] = img
        # print(img)
        # print(item)
        item['category1'], item['title'], item['abstract'], item['body'] = \
            self.formalize(item['category1'], title, None, body, item['language_id'])
        if item['body'] is not None and len(item['body']) > 2:
            yield item
        # print(self.cnt)
