
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
from scrapy import FormRequest
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from scrapy.http import Request, Response
import re
import scrapy
import time
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

# author 武洪艳
class PaukphawcnSpider(BaseSpider):
    name = 'paukphawcn'
    # allowed_domains = ['www.paukphaw.cn/']
    start_urls = ['http://www.paukphaw.cn/']  # http://www.paukphaw.cn/
    website_id = 1462  # 网站的id(必填)
    language_id = 1813  # 语言
    is_http = 1
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'root',
    #     'password': 'why520',
    #     'db': 'dg_crawler'
    # }

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#navbarCollapse > ul > li > ul.dropdown-menu > li a')
        for category in categories:
            category_url = 'http://www.paukphaw.cn' + category.get('href')
            yield Request(url=category_url, callback=self.parse_page, meta={'category2': category.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        global last_time
        if soup.select('div.col-md-9 .list.list-condensed .items.items-hover .item .item-heading span:nth-child(3)') != []:
            last_time = soup.select('div.col-md-9 .list.list-condensed .items.items-hover .item .item-heading span:nth-child(3)')[-1].text.strip() + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.format_time3(last_time) >= int(OldDateUtil.time):
            articles = soup.select('div.col-md-9 .list.list-condensed .items.items-hover .item .item-heading > h4 > a')
            for article in articles:
                article_url = 'http://www.paukphaw.cn' + article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            # pages = int(soup.select_one('div.col-md-9 > div > footer > div > strong:nth-child(3)').text.split('/')[1])
            # for i in range(1, pages + 1):
            if soup.select('div.col-md-9 > div > footer > div > a') != []:
                next_page = 'http://www.paukphaw.cn' + soup.select('div.col-md-9 > div > footer > div > a')[-2].get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        if soup.select_one('body > div.page-container > div > div > ul > li:nth-child(2) > a') is not None:
            item['category1'] = soup.select_one('body > div.page-container > div > div > ul > li:nth-child(2) > a').text
        item['category2'] = response.meta['category2']
        if soup.select_one('div.page-container .col-md-9 > div.article > header > h1') is not None:
            item['title'] = soup.select_one('div.page-container .col-md-9 > div.article > header > h1').text.strip(' ')
        if soup.select_one('div.col-md-9 > div.article > header > dl > dd:nth-child(1)') is not None:
            item['pub_time'] = soup.select_one('div.col-md-9 > div.article > header > dl > dd:nth-child(1)').text
        else:
            item['pub_time'] = OldDateUtil.format_time()
        image_list = []
        imgs = soup.select('div.col-md-9 > div.article > section.article-content > p img')
        if imgs:
            for img in imgs:
                if img.get('src').split('/')[1] == 'data':
                    image_list.append('http://www.paukphaw.cn' + img.get('src'))
                else:
                    image_list.append(img.get('src'))
            item['images'] = image_list
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('div.col-md-9 > div.article > section.article-content p') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        # item['abstract'] = soup.select_one('div.col-md-9 > div.article > section.article-content > p:nth-child(3)').text
        return item

