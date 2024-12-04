# encoding: utf-8
import html

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
import sys


# author : 张鸿兴
class SmggovSpider(BaseSpider):  # 类名重命名
    author = "张鸿兴"
    name = 'smggov'  # name的重命名
    language_id = 2122
    website_id = 2171  # id一定要填对！
    allowed_domains = ['smg.gov.mo']
    start_urls = ['https://cms.smg.gov.mo/pt/api/news/news',
                  'https://cms.smg.gov.mo/en/api/news/news',
                  'https://cms.smg.gov.mo/zh_TW/api/news/news']
    lan_num = 3

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
        body = re.sub('<br>.*?<br>', '\n', body)
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
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        if language_id == 1813:
            title = convert(title, 'zh-cn')
            abstract = convert(abstract, 'zh-cn')
            body = convert(body, 'zh-cn')
        return title, abstract, body

    def parse(self, response):
        url = response.request.url
        if "pt" in url:
            self.language_id = 2122
        elif "en" in url:
            self.language_id = 1866
        elif "zh_TW" in url:
            self.language_id = 1813
        yield scrapy.Request(url=url, callback=self.parse_news_id, meta={})

    def parse_news_id(self, response):
        res = response.request.url
        response = response.json()
        for i in range(0, len(response)):
            # print(response[i])
            pub_time = response[i].get('startdate')
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            news_id = response[i].get('id')
            url = res[0:res.find('news/') + 5] + str(news_id)
            # print(url)
            yield scrapy.Request(url=url, callback=self.parse_item, meta={})

    def parse_item(self, response):
        res = response.request.url
        response = response.json()[0]
        url1 = res[0:res.find('news/') + 5]
        item = NewsItem(language_id=self.language_id)
        if "pt" in url1:
            self.language_id = 2122
            item['language_id'] = 2122
        elif "en" in url1:
            self.language_id = 1866
            item['language_id'] = 1866
        elif "zh_TW" in url1:
            self.language_id = 1813
            item['language_id'] = 1813
        if self.language_id == 2122:
            item['category1'] = response.get('referNews').get('namePt')
            body_text = response.get('translations').get('pt')
        elif self.language_id == 1866:
            item['category1'] = response.get('referNews').get('nameEn')
            body_text = response.get('translations').get('en')
        elif self.language_id == 1813:
            item['category1'] = response.get('referNews').get('name')
            body_text = response.get('translations').get('zh_TW')
        # print(body_text)
        pub_time = response.get('startdate')
        item['pub_time'] = pub_time
        title = body_text.get('title')
        body_html = body_text.get('content')
        # print(body_html)
        abstract = None
        if body_html is None:
            pass
        else:
            html_to_list = re.findall(r'>(.*)<', str(body_html))
            # print("------------------------------------")
            # print(html_to_list)
            # print("------------------------------------")
            bodytext = ""
            for text in html_to_list:
                # print(text)
                text = text.replace("&nbsp;", "\n")
                if '<img' not in text and '<iframe' not in text:
                    bodytext += text + '\n'
            # print(bodytext)
            # print("-------------------------------------")
            if '<span' in bodytext:
                html_to_string_replace_list = []
                html_to_string_replace_list += re.findall(r'(<.*?>)', bodytext)
                # print(html_to_string_replace_list)
                for i in html_to_string_replace_list:
                    bodytext = bodytext.replace(i, '')
            # print(bodytext)
            body = '\n'.join(line for line in bodytext.split('\n') if line)
            # print(body)
            href = re.findall(r'<a href.*?>', body)
            # print(href)
            if href is not None:
                for h in href:
                    body = body.replace(h, '')
            # print(body)
            body = html.unescape(body)
            body = body.replace('<strong>', '')
            body = body.replace('</strong>', '')
            body = body.replace('</a>', '')
            body = body.replace('<a>', '')
            body = body.replace('<sup>', '')
            body = body.replace('</sup>', '')
            body = body.replace('<!--', '')
            body = re.sub('<[^>]+>', '', body)
            body = body.strip()
            # print('---------')
            # print(len(body))
            # print('---------')
            if len(body) == 0:
                pass
            else:
                abstract = body.split('\n')[0]
                imglist = re.findall(r'src="(.*?)"', str(body_html))
                # print(imglist)
                # print(len(imglist))
                img = []
                for i in range(0, len(imglist)):
                    # print(imglist[i])
                    if 'youtube' not in imglist[i]:
                        img.append(imglist[i])
                # print(img)
                item['images'] = img
                item['title'], item['abstract'], item['body'] = self.formalize(title, None, body, item['language_id'])
                if item['body'] is not None and len(item['body']) > 2:
                    yield item
