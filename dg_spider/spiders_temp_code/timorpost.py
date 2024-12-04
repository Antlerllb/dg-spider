import html
import scrapy
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
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
from lxml import etree



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
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re


class TimorpostSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    name = 'timorpost'  # name的重命名
    language_id = 2122
    website_id = 369  # id一定要填对！
    start_urls = ['https://en.timorpost.com/indeks/page/1/', 'https://pt.timorpost.com/indeks/page/1/']
    url1 = 'https://timorpost.com/indeks/page/'
    url2 = ''
    m_pt = OldDateUtil.PT_2122_DATE
    m_en = OldDateUtil.EN_1866_DATE

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
        soup = BeautifulSoup(response.text, 'html.parser')
        url = response.request.url
        # print(url)
        if "pt." in url:
            language_id = 2122
            response.meta['end_page'] = int(soup.select('#primary > nav > div > a')[1].text)
            # print(response.meta['end_page'])
        else:
            language_id = 1813
            response.meta['end_page'] = 1
        response.meta['page'] = 1
        response.meta['url'] = url[0:] + 'page/' + str(response.meta['page']) + '/'
        # print(response.meta['url'])
        response.meta['lan_id'] = language_id
        # print(soup.select('#primary > nav > div > a'))
        yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)

    def parse_pages(self, response):
        end_page = response.meta['end_page']
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('article')
        # print(block)
        for i in block:
            # break
            time_list = re.sub(r'\t', '', i.select_one('time').text.strip())
            time_list = re.sub('\n+', '\n', time_list)
            time_list = re.split(' ', time_list)
            response.meta[
                'pub_time'] = f'{time_list[2]}-{str(self.m_en[time_list[1]]).zfill(2)}-{time_list[0].zfill(2)} 00:00:00'
            # print(response.meta['pub_time'])
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(response.meta['pub_time']) < OldDateUtil.time:
                return
            response.meta['category1'] = i.select_one('span.cat-links-content > a').text.strip()
            response.meta['title'] = i.select_one('h2 > a').text
            # print(response.meta['category1'])
            # print(response.meta['title'])
            href = i.select_one('h2 > a')['href']
            # print(href)
            # href = 'https://timorpost.com/arte/tp-40405/asnm-sei-kuda-nuu-25-hektares/'
            yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)
        # 翻页操作：
        # print(end_page)
        if response.meta['page'] < end_page:
            # 1. 不断增加页码数
            response.meta['page'] += 1
            # 2. 拼接url
            url = response.meta['url']
            # print(url)
            url1 = url[0:url.find('/page') + 6]
            url2 = ''
            url = url1 + str(response.meta['page']) + url2 + '/'
            # print(url)
            # print(url)
            # 3. 回调parse_page函数
            yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)

    def parse_items(self, response):  # 主页，用于点进每个菜单
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        body = ''.strip()
        article = soup.select_one('div.single-wrap > div').text.strip()
        article = re.sub('\n+', '\n', article)
        article = re.sub(' \n', '', article)
        article = article.replace('SCROLL FILA BA NOTISIA', '').replace('ADVERTISEMENT', '')
        article = article.split('\n')
        for i in article:
            if 'total views,' in i:
                break
            body += i.strip().replace('\n', '') + '\n'
        # print(body)
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['language_id'] = response.meta['lan_id']
        img_list = soup.select_one('figure > img')
        img = []
        if img_list is not None:
            if img_list['src'] != '':
                image = img_list['src']
                if 'www' in image:
                    img.append(image)
                else:
                    img.append(image[:image.find('s://') + 4] + 'www.' + image[image.find('s://') + 4:])
        item['images'] = img
        # print(img)
        item['category1'], item['title'], item['abstract'], item['body'] = \
            self.formalize(item['category1'], item['title'], None, body, item['language_id'])
        if item['body'] is not None and len(item['body']) > 2:
            # print(item['body'])
            yield item
