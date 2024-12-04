import html
import random

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


class PerugobSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    name = 'perugob'  # name的重命名
    language_id = 2181
    website_id = 1303  # id一定要填对！
    start_urls = ['https://www.gob.pe/busquedas.json?contenido=noticias&sheet=1&sort_by=recent']
    url1 = 'https://www.gob.pe/busquedas.json?contenido=noticias&sheet='
    url2 = '&sort_by=recent'
    page = 1
    m_es = OldDateUtil.ES_2181_DATE

    @staticmethod
    def is_only_symbols(string):
        pattern = r'^[^\w\s]+$'  # 匹配只包含符号的模式
        match = re.match(pattern, str(string))
        return match is not None

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
        title = re.sub(' +', ' ', title).strip().strip('\n').replace('\n', '')
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
        body = PerugobSpider.remove_emoji(body)
        
        title = OldFormatUtil.remove_invalid_utf8(title)
        body = OldFormatUtil.remove_invalid_utf8(body)
        body = re.sub(' +', ' ', body).strip()
        body = body.strip().strip('\n')
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        if language_id == 1813:
            category, title, abstract, body = convert(category, 'zh-cn'), convert(title, 'zh-cn'), \
                                              convert(abstract, 'zh-cn'), convert(body, 'zh-cn'),
        return category, title, abstract, body

    def parse(self, response):
        res = response.json()
        is_exsist = res.get('error')
        if is_exsist is not None:
            pass
        else:
            block = res.get('data').get('attributes').get('results')
            # print(len(block))
            item = NewsItem(language_id=self.language_id)
            if block is None or len(block) == 0:
                return
            for i in block:
                # break
                time_list = i.get('publication')
                if time_list is None:
                    pass
                else:
                    time_list = time_list.split('-')[0].replace(' de ', ' ').strip().replace('setiembre', 'septiembre')
                    time_list = time_list.split(' ')
                    # print(time_list)
                    response.meta[
                        'pub_time'] = f'{time_list[2]}-{str(self.m_es[time_list[1].capitalize()]).zfill(2)}-{time_list[0].zfill(2)} 00:00:00'
                    # print(item['pub_time'])
                    if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(
                            response.meta['pub_time']) < OldDateUtil.time:
                        return
                    if i.get('url') is not None and i.get('name_with_parent') is not None:
                        response.meta['language_id'] = 2181
                        cate = i.get('group_type')
                        if cate is not None:
                            response.meta['category1'] = i.get('group_type')
                            # print(item['category1'])
                        else:
                            response.meta['category1'] = 'Noticias'
                        response.meta['title'] = i.get('name_with_parent')
                        # print(item['title'])
                        news = i.get('url')
                        href = 'https://www.gob.pe/' + news[news.find('href="') + 6:news.find('">')]
                        href = href.split('-')[0]
                        # print(href)
                        # href = 'https://www.gob.pe//institucion/ugelchulucanas/noticias/823473'
                        yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)
                        # return
        # 翻页操作：
        # 1. 不断增加页码数
        self.page += 1
        # 2. 拼接url
        url = self.url1 + str(self.page) + self.url2
        # print(url)
        # 3. 回调parse_page函数
        yield scrapy.Request(url=url, callback=self.parse, meta=response.meta)

    def parse_items(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        url = response.request.url
        # print(url)
        body = soup.select_one('#main > section > div > div > div').text.replace('  ', '\n')
        # print(body)
        item['category1'], item['title'], item['abstract'], item['body'] = \
            self.formalize(response.meta['category1'], response.meta['title'], None, body, response.meta['language_id'])
        # j = i.get('pic')
        j = soup.select('img.img-responsive.shadow-feed-img')
        img = []
        if j is not None:
            for _ in j:
                if len(_['src']) > 5:
                    if 'https' in _['src']:
                        img.append(_['src'])
        item['images'] = img
        item['pub_time'] = response.meta['pub_time']
        # print(item)
        item['body'] = item['body'].strip('\n').strip()
        if item['body'] is not None and len(item['body']) > 100:
            if item['abstract'] is not None and len(item['abstract']) > 2:
                body = item['body']
                # print(body)
                if re.findall('\n', str(body)) is not None:
                    if self.is_only_symbols(str(body)) is False:
                        if len(body.split('\n')) > 1:
                            yield item