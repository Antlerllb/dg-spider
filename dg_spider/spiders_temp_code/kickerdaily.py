
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

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil as bs
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

class KickerdailySpider(BaseSpider):
    name = 'kickerdaily'
    allowed_domains = ['kickerdaily.com']
    start_urls = [#'http://kickerdaily.com/',
                  'https://kickerdaily.com/posts/category/tagalog/',
                  'https://kickerdaily.com/posts/category/philippines/',
                  'https://kickerdaily.com/posts/category/world/',
                  'https://kickerdaily.com/posts/category/entertainment-world/',
                  'https://kickerdaily.com/posts/category/social-news/']
    website_id = 496
    language_id = 1880
    # proxy = '01'
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    def parse(self, response):
        meta = {}
        soup = bs(response.text,"html.parser")
        category1 = soup.find("h1",class_="page-title").text.strip()
        meta["category1"] = category1
        meta["category2"] = None
        url_list = soup.select("#main-content > article")
        for h in url_list:
            news_url = h.find(class_="entry-title mh-posts-list-title").find("a").get("href")
            yield scrapy.Request(news_url,callback=self.parse_news,meta=meta)
        pub_time = soup.select("#main-content > article")[-1].find(class_="mh-meta-date updated").text
        if OldDateUtil.time == None or OldDateUtil.format_time3(OldDateUtil.format_time2(pub_time)) >= int(OldDateUtil.time):
            yield scrapy.Request(soup.select('a.next.page-numbers')[0].attrs['href'], callback=self.parse)
        else:
            self.logger.info('时间截止')

    def parse_news(self,response):
        item = NewsItem(language_id=self.language_id)
        soup = bs(response.text,"html.parser")
        item["category1"] = response.meta["category1"]
        item["category2"] = response.meta["category2"]
        pub_time = soup.find("span","entry-meta-date updated").find("a").text.strip() if soup.find("span","entry-meta-date updated") else "0000-00-00 00:00:00"
        if pub_time:
            item["pub_time"] = OldDateUtil.format_time2(pub_time)

        div = soup.find("div",class_="entry-content clearfix")
        images = [img.get("src") for img in div.find_all("img")] if div.find_all("img") else None
        item["images"] = images
        title = soup.find("h1",class_="entry-title").text.strip()
        item["title"] = title
        abstract1 = [a.text.strip() for a in div.find_all("li") ]if div.find_all("li") else div.find("p").text.strip()
        abstract = ''
        for a in abstract1:
            abstract += a
        item["abstract"] = abstract
        body = [p.text.strip() for p in div.find_all("p")] if div.find_all("p") else None
        body = "\n".join(body)
        item["body"] = body
        yield item
