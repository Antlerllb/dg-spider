
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


# author: 陈宝胜
class ThemalaysianreserveSpider(BaseSpider):
    name = 'themalaysianreserve'
    website_id = 173  # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    start_urls = ['https://themalaysianreserve.com/']
    # sql = {  # sql配置
    #     'host': '121.36.242.178',
    #     'user': 'dg_cbs',
    #     'password': 'dg_cbs',
    #     'db': 'dg_test_source'
    # }

    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
          
        

    def parse(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for category_url in [a.get("href") for a in
                             soup.select_one(".main-menu ul#menu-primary-menu").find_all("a", itemprop="url")[1:-2]]:
            yield scrapy.Request(category_url, callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features='lxml')
        for news_url in [a.get("href") for a in soup.select(".container .col-md section > div > a")]:
            yield scrapy.Request(news_url, callback=self.parse_detail)
        next_page = soup.select(".col-12.paging .col-auto")[0].select_one("a").get("href") if \
        soup.select(".col-12.paging .col-auto")[0].select_one("a") else None
        LastTimeStamp = OldDateUtil.format_time3(str(datetime.strptime(
            soup.select(".container .col-md section > div > a span.trend-date")[-1].text.split(",", 1)[1].replace("th","").replace("nd", "").replace("rd", "").replace("st", "").replace("Augu", "August").strip(), "%B %d, %Y")))
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
        item['title'] = soup.select_one(".single-post h2").text.strip()
        item['category1'] = soup.select(".article .breadcrumb-item a")[1].text
        item['category2'] = soup.select(".article .breadcrumb-item a")[2].text if len(
            soup.select(".article .breadcrumb-item a")) == 3 else None
        item['pub_time'] = str(datetime.strptime(soup.select_one("p.editor-info time").get("datetime"), "%Y-%m-%d"))
        item['body'] = "\n".join(p.text.strip() for p in soup.select(".single-post-content.clearfix div.dable-content-wrapper > p")) if soup.select(".single-post-content.clearfix div.dable-content-wrapper > p") else "\n".join(div.text.strip() for div in soup.find_all("div", dir="auto"))
        item['abstract'] = soup.select(".single-post-content.clearfix div.dable-content-wrapper > p")[1].text.strip() if soup.select(".single-post-content.clearfix div.dable-content-wrapper > p") else soup.find_all("div", dir="auto")[1].text.strip()
        item['images'] = [img.get("src") for img in soup.select(".single-post .feature-img img")] if soup.select(".single-post .feature-img img") else [img.get("src") for img in soup.select(".single-post .featured-image img")]
        item['website_id'] = self.website_id
        item['language_id'] = self.language_id
        item['request_url'] = response.request.url
        item['response_url'] = response.url
        item['cole_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        yield item