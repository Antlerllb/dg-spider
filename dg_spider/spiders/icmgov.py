# encoding: utf-8
import datetime
import html

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
from scrapy.utils import spider




from scrapy.http.request import Request
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
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


# author : 张鸿兴
class IcmgovSpider(BaseSpider):  # 类名重命名
    author = "张鸿兴"
    name = 'icmgov'  # name的重命名
    language_id = 2122
    website_id = 2165  # id一定要填对！
    pages = 1
    now_year = int(str(datetime.datetime.now())[0:4])
    start_urls = ['https://www.icm.gov.mo/gb/newsPart/',
                  'https://www.icm.gov.mo/pt/newsPart/',
                  'https://www.icm.gov.mo/en/newsPart/']

    @staticmethod
    def formalize(title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ')
        title = title.replace('\t', ' ')
        title = title.replace('\u3000', ' ')
        title = title.replace(' ', ' ')
        title = title.replace('\n', '')
        title = re.sub(' +', ' ', title)
        title = title.strip().strip('\n')
        body = re.sub('<br>　　<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', ' ')
        body = body.replace('\t', ' ')
        body = body.replace('\u3000', ' ')
        body = body.replace(' ', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub(' +', ' ', body)
        body = body.strip()
        if language_id == 1813:
            body = convert(body, 'zh-cn')
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        abstract = re.sub('<[^>]+>', '', abstract)
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        return title, abstract, body

    def parse(self, response):
        response.meta['url_pre'] = response.request.url
        url = response.request.url + str(self.now_year) + '/' + str(self.pages) + '/0/'
        response.meta['url'] = url
        if "pt" in url:
            response.meta['language_id'] = 2122
        elif "gb" in url:
            response.meta['language_id'] = 1813
        elif "en":
            response.meta['language_id'] = 1866
        # print(url)
        yield scrapy.Request(url=url, callback=self.parse2, meta=response.meta)

    def parse2(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('div.row.text-center')
        if len(block) != 0:
            self.pages += 1
            if OldDateUtil.time is not None:
                time_list = block[0].select_one('div.col-sm-3.col-xs-12.text-right').text.strip().split('/')
                last_time = f'{time_list[2]}-{time_list[1]}-{time_list[0]} 00:00:00'
                # print(last_time)
                if OldDateUtil.str_datetime_to_timestamp(last_time) < OldDateUtil.time:
                    return
            for i in block:
                time_list = i.select_one('div.col-sm-3.col-xs-12.text-right').text.strip().split('/')
                pub_time = f'{time_list[2]}-{time_list[1]}-{time_list[0]} 00:00:00'
                response.meta['pub_time'] = pub_time
                if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                    return
                response.meta['title'] = i.select_one('h4').text.replace('\r', '').replace('\n', ' ')
                href = 'https://www.icm.gov.mo' + i.select_one('a')['href']
                # print(href)
                response.meta['abstract'] = i.select_one('p').text.strip()
                yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)
        else:
            self.pages = 1
            self.now_year -= 1
        url = response.meta['url_pre'] + str(self.now_year) + '/' + str(self.pages) + '/0/'
        # print(url)
        yield scrapy.Request(url=url, callback=self.parse2, meta=response.meta)

    def parse_items(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['language_id'] = response.meta['language_id']
        item['category1'] = soup.select_one('#ctl00_bodyCPH_catName').text
        if item['category1'] is None or len(item['category1']) <= 1:
            item['category1'] = '---'
        body = soup.select_one('#ctl00_bodyCPH_newsContent_L').text.strip()
        abstract = response.meta['abstract']
        if len(abstract) == 0:
            abstract = body.split('\n')[0]
        title = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        img_list = soup.select('#ctl00_bodyCPH_newsContent_L > div > img')
        images = []
        for i in img_list:
            images.append(i['src'])
        item['images'] = images
        item['title'], item['abstract'], item['body'] = self.formalize(title, abstract, body, item['language_id'])
        # print(item)
        yield item
