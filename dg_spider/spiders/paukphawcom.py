
from dg_spider.items import NewsItem
import scrapy
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
class PaukphawcomSpider(BaseSpider):
    name = 'paukphawcom'
    # allowed_domains = ['www.paukphaw.com/']
    start_urls = ['http://www.paukphaw.com/']  # http://www.paukphaw.com/
    website_id = 1463  # 网站的id(必填)
    language_id = 2065  # 语言
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
        categories = soup.select('#navbarCollapse > ul > li > a')[1:8]
        for category in categories:
            category_url = 'http://www.paukphaw.com' + category.get('href')
            meta = {'category1': category.text, 'category2': None}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        if soup.select('div.col-md-9 .list.list-condensed .items.items-hover .item .item-heading span:nth-child(3)') != []:
            last_time = soup.select('div.col-md-9 .list.list-condensed .items.items-hover .item .item-heading span:nth-child(3)')[-1].text.strip() + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.format_time3(last_time) >= int(OldDateUtil.time):
            articles = soup.select('div.col-md-9 .list.list-condensed .items.items-hover .item .item-heading > h4 > a')
            for article in articles:
                article_url = 'http://www.paukphaw.com' + article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select('div.col-md-9 > div > footer > div > a') != []:
                next_page = 'http://www.paukphaw.com' + soup.select('div.col-md-9 > div > footer > div > a')[-2].get( 'href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        if soup.select_one('div.page-container div.col-md-9 > div.article > header > h1') is not None:
            item['title'] = soup.select_one('div.page-container div.col-md-9 > div.article > header > h1').text
        if soup.select_one('div.col-md-9 > div.article > header > dl > dd:nth-child(1)') is not None:
            item['pub_time'] = soup.select_one('div.col-md-9 > div.article > header > dl > dd:nth-child(1)').text
        else:
            item['pub_time'] = OldDateUtil.format_time()
        image_list = []
        imgs = soup.select('div.col-md-9 > div.article > section.article-content img')
        if imgs:
            for img in imgs:
                if img.get('src').split('/')[1] == 'data':
                    image_list.append('http://www.paukphaw.com' + img.get('src'))
                else:
                    image_list.append(img.get('src'))
            item['images'] = image_list
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in
             soup.select('div.col-md-9 > div.article > section.article-content') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        # if soup.select_one('div.col-md-9 > div.article > header > section') is None:
        #     item['abstract'] = p_list[0]
        # else:
        #     item['abstract'] = soup.select_one('div.col-md-9 > div.article > header > section').text.split(':')[1]
        return item