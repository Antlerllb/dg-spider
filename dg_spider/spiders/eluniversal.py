import html
import json
import urllib.parse

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
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re


class EluniversalSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    name = 'eluniversal'
    language_id = 2181
    website_id = 1308
    start_urls = ['https://www.eluniversal.com/buscador']
    page = 3
    flag = 0
    m_pt = OldDateUtil.PT_2122_DATE
    m_en = OldDateUtil.EN_1866_DATE

    @staticmethod
    def remove_emoji(text):
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|"
            "[\U0001F700-\U0001F77F]|[\U0001F780-\U0001F7FF]|[\U0001F800-\U0001F8FF]|"
            "[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FA6F]|[\U0001FA70-\U0001FAFF]|"
            "[\U00002702-\U000027B0]|[\U000024C2-\U0001F251]",
            flags=re.UNICODE)
        return emoji_pattern.sub('', text)

    @staticmethod
    def formalize(category, title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ').replace('\n', '')
        title = re.sub(' +', ' ', title).strip().strip('\n')
        body = re.sub('<br>.*?<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', '').replace('\t', '').replace('\u3000', ' ').replace(' ', ' ').replace('　', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = re.sub(' +', ' ', body).strip()
        body = body.strip().split('\n')
        body_list = []
        for _ in body:
            body_list.append(_.strip())
        body = '\n'.join(body_list)
        body = re.sub(' \n', '', body).strip('\n')
        body = EluniversalSpider.remove_emoji(body)
        body = OldFormatUtil.remove_invalid_utf8(body)
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        abstract = abstract.strip()
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        if language_id == 1813:
            category, title, abstract, body = convert(category, 'zh-cn'), convert(title, 'zh-cn'), \
                                              convert(abstract, 'zh-cn'), convert(body, 'zh-cn'),
        return category, title, abstract, body

    def parse(self, response):
        url = 'https://www.eluniversal.com/buscador'
        data = {
            'query': '',
            'pagina': str(self.page),
            'seccioncod': '01-HOME'
        }
        # data = json.dumps(data)
        # print(data)
        # yield scrapy.Request(url=url, body=data, method="POST", callback=self.parse_page)
        yield scrapy.FormRequest(url=url, formdata=data, callback=self.parse_page)
        self.page += 1
        pre1 = 'https://www.gob.pe/busquedas.json?contenido=noticias&sheet='
        pre2 = '&sort_by=recent'
        back = pre1 + str(self.page) + pre2
        # print(back)
        # if self.page < 200:
        if self.flag == 0:
            yield scrapy.Request(url=back, callback=self.parse, meta=response.meta)

    def parse_page(self, response):
        # print(self.page)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        # return
        block = soup.select_one('div.row.row-eq-height-resp.main-news.hidden-xs.hidden-sm').select(
            'div.col-xs-12.pdd-0.article-back.icon-space')
        # print(block)
        # return
        item = NewsItem(language_id=self.language_id)
        if block is None or len(block) == 0:
            return
        for i in block:
            # break
            time_list = i.select_one('p.hora').text.split(' ')[0].split('/')
            # print(time_list)
            response.meta['pub_time'] = f'{time_list[2]}-{time_list[1].zfill(2)}-{time_list[0].zfill(2)} 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(response.meta['pub_time']) < OldDateUtil.time:
                self.flag = 1
                return
            response.meta['title'] = i.select_one('span.ellip').text.strip()
            # print(response.meta['title'])
            main_part = i.select_one('div.bg-img-container.img-container.img-bg')
            response.meta['category1'] = i.select_one('span.c1').text.replace('\t', '').replace('\r', '')
            response.meta['category1'] = re.sub(' +', ' ', response.meta['category1']).strip()
            # print(response.meta['category1'])
            # return
            response.meta['img'] = []
            images = main_part.select('img')
            if images is not None and len(images) > 0:
                for j in images:
                    image = j['src'].strip()
                    if image is not None:
                        if 'http' in image:
                            response.meta['img'].append(image)
                        else:
                            response.meta['img'].append('https:' + image)
            # print(response.meta['img'])
            href = main_part.select_one('a')
            if href is not None:
                href = href['href']
                # print(href)
                yield scrapy.Request(url=href, callback=self.parse_item, meta=response.meta)
            # return

    def parse_item(self, response):
        # print(response)
        # return
        # print(response.text)
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        # return
        item['abstract'] = soup.select_one('#sumario')
        if item['abstract'] is not None:
            item['abstract'] = item['abstract'].text.strip()
            article = soup.select_one('#cuerpo')
            # print(article)
            # return
            body = ''
            if article is not None:
                for t in article:
                    body += t.text.strip()
                    body += '\n'
            item['pub_time'] = response.meta['pub_time']
            item['language_id'] = self.language_id
            item['category1'] = response.meta['category1']
            item['title'] = response.meta['title']
            item['category1'], item['title'], item['abstract'], item['body'] = \
                self.formalize(item['category1'], item['title'], item['abstract'], body, item['language_id'])
            item['images'] = response.meta['img']
            # print(item['body'])
            if item['body'] is not None and len(item['body']) > 100:
                if len(body.split('\n')) != 1:
                    if item['abstract'] is not None and len(item['abstract']) > 20:
                        yield item
