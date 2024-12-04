# encoding: utf-8
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


# author : 张鸿兴
class SmgSpider(BaseSpider):  # 类名重命名
    name = 'smg'  # name的重命名
    language_id = 0
    website_id = 2171  # id一定要填对！
    allowed_domains = ['smg.gov.mo']
    number = 450
    start_urls = ['https://cms.smg.gov.mo/pt/api/news/' + str(number),
                  'https://cms.smg.gov.mo/en/api/news/' + str(number),
                  'https://cms.smg.gov.mo/zh_TW/api/news/' + str(number)]

    # start_urls = ['https://cms.smg.gov.mo/zh_TW/api/news/news', 'https://cms.smg.gov.mo/en/api/news/news',
    #               'https://cms.smg.gov.mo/pt/api/news/news']

    def parse(self, response):
        res = response.request.url
        url1 = res[0:res.find('news/') + 5]
        if "pt" in url1:
            self.language_id = 2122
            start_url = 'https://cms.smg.gov.mo/pt/api/news/news'
        elif "en" in url1:
            self.language_id = 1866
            start_url = 'https://cms.smg.gov.mo/en/api/news/news'
        elif "zh_TW" in url1:
            self.language_id = 1813
            start_url = 'https://cms.smg.gov.mo/zh_TW/api/news/news'
        yield scrapy.Request(url=start_url, callback=self.parse2, meta={})

    def parse2(self, response):
        res = response.request.url
        response = response.json()[0]
        recent_news_num = response.get('id')
        self.number = int(recent_news_num)
        url = res[0:res.find('news/')+5] + str(recent_news_num)
        # print(url)
        yield scrapy.Request(url=url, callback=self.parse3, meta={})

    def parse3(self, response):  # 主页，用于点进每个菜单
        res = response.request.url
        # print(res)
        number = self.number
        # print(number)
        response = response.json()
        # print(response)
        # print(type(response))
        while number >= 1:
            if type(response) is dict:
                flag = 0
                number -= 1
            else:
                item = NewsItem(language_id=self.language_id)
                response = response[0]
                # print(type(response))
                pub_time = response.get('startdate')
                url1 = res[0:res.find('news/') + 5]
                if "pt" in url1:
                    self.language_id = 2122
                elif "en" in url1:
                    self.language_id = 1866
                elif "zh_TW" in url1:
                    self.language_id = 1813
                # print(pub_time)
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= OldDateUtil.time:  # 判断是否是最新的新闻
                    item['pub_time'] = pub_time
                    # print(response)
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
                    title = body_text.get('title')
                    item['title'] = title
                    body_html = body_text.get('content')
                    # print(body_html)
                    if body_html is None:
                        flag = 0
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
                        body = body.strip()
                        # print('---------')
                        # print(len(body))
                        # print('---------')
                        if len(body) == 0:
                            flag = 0
                            pass
                        else:
                            item['body'] = body
                            item['abstract'] = item['body'].split('\n')[0]
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
                            number -= 1
                            flag = 1
                else:
                    break
            # print(res)
            url1 = res[0:res.find('news/') + 5]
            url = url1 + str(number)
            # print(url)
            if flag:
                # print(item)
                yield item
            yield scrapy.Request(url=url, callback=self.parse3, meta={})
