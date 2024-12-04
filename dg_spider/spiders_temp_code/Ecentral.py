
# 此文件包含的头文件不要修改
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

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http import Request, Response
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re
import scrapy
import requests

# author: 陈宝胜
def get_LastTimeStamp(url):
    # 请求网页获取时间戳
    soup = BeautifulSoup(requests.get(url).text, features="lxml")
    return OldDateUtil.format_time3(soup.select_one("article .entry-meta time").get("datetime").replace("T", " ").split("+")[0])


# 将爬虫类名和name字段改成对应的网站名
class EcentralSpider(BaseSpider):
    name = 'Ecentral'
    website_id = 171  # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    start_urls = ['https://ecentral.my/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for category_url in [a.get("href") for a in soup.select(".main-nav ul#menu-main-menu-1 > li > a")[1:2]]:
            yield scrapy.Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        news_list = soup.select("#main article h2 a")
        for news_url in [a.get("href") for a in news_list]:
            yield scrapy.Request(news_url, callback=self.parse_detail)
        LastTimeStamp = get_LastTimeStamp(news_list[-1].get("href"))
        next_page = soup.select_one(".nav-links a.next.page-numbers").get("href") if soup.select_one(".nav-links a.next.page-numbers") else None
        if OldDateUtil.time is None or LastTimeStamp >= OldDateUtil.time:
            if next_page:
                yield scrapy.Request(next_page, callback=self.parse_category)
            else:
                self.logger.info("该目录已经到底")
        else:
            self.logger.info("时间截止")

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        item = NewsItem(language_id=self.language_id)
        item['pub_time'] = soup.select_one("article .entry-meta time").get("datetime").replace("T", " ").split("+")[0]
        item['title'] = soup.select_one(".entry-header h1").text.strip()
        item['body'] = "\n".join([p.text.strip() for p in soup.select(".entry-content > p")])
        item['abstract'] = soup.select_one(".entry-content > p").text.strip()
        item['images'] = [img.get("data-lazy-src") for img in soup.select(".entry-content > figure img")]
        item['category1'] = soup.select("#main p#breadcrumbs a")[-1].text
        item['category2'] = None
        item['website_id'] = self.website_id
        item['language_id'] = self.language_id
        item['request_url'] = response.request.url
        item['response_url'] = response.url
        item['cole_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        yield item

