
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
class ThaicnnetnewsSpider(BaseSpider):
    name = 'thaicnnetnews'
    # allowed_domains = ['www.thaicn.net/news/']
    start_urls = ['http://www.thaicn.net/news/']  # http://www.thaicn.net/news/
    website_id = 1603  # 网站的id(必填)
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

    # 这是类初始化函数，用来传时间戳参数


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        if soup.select('.news_list table:nth-child(2) tr:nth-child(3) table .epages a')[-1].text == '尾页':
            articles = soup.select('.news_list table:nth-child(2) tr:nth-child(3) table a')[:80]
        else:
            articles = soup.select('.news_list table:nth-child(2) tr:nth-child(3) table a')[:28]
        flag = True
        if OldDateUtil.time is not None:  # 加一句这个判断，没有给时间戳参数时候，就不用去搜索last_time,运行快一些。
            last_time = articles[-1].get('href').split('/')[-2] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.format_time3(last_time) >= int(OldDateUtil.time):
            for article in articles:
                article_url = article.get('href')
                meta = {'pubtime': article_url.split('/')[-2] + ' 00:00:00'}
                yield Request(url=article_url, callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = soup.select('.news_list table:nth-child(2) tr:nth-child(3) table .epages a')[-2].get('href') if \
                soup.select('.news_list table:nth-child(2) tr:nth-child(3) table .epages a') else None # 判断下一页，可以加个if else在后面，三目运算符。
            yield Request(url=next_page, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = soup.select_one('td.main > table.position a:nth-child(3)').text
        item['title'] = soup.select_one('td.main > table:nth-child(2) font').text
        item['pub_time'] = response.meta['pubtime']
        item['images'] = ['http://www.thaicn.net' + img.get('src') for img in soup.select('td.main > table:nth-child(2) p img')]
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('#text') if paragraph.text!='' and paragraph.text!=' '])
        # 感受一下65 66行的处理，注意细节。你的代码太多啦！
        item['abstract'] = item['body'].split('\n')[0]
        yield item