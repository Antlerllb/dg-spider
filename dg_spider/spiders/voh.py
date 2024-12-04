from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy

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
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
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


# 以下的头文件不要修改




#author:马嘉颖
# check: 凌敏 pass
class VohSpider(BaseSpider):
    name = 'voh'
    website_id = 266  # 网站的id(必填)
    language_id = 2242  # 所用语言的id
    start_urls = ['https://voh.com.vn']


    def parse(self, response):
        ca= response.xpath("//div[@class='NavigationDefault_desktop__3ByWL']/h5[@class='style_html-tag-h5__8ufRl']/a")
        for i in ca:
            u = i.xpath("./@href").extract()[0]
            if "//" not in u and "739" not in u:#排除某些类别
                c=i.xpath("./text()").extract()[0]
                yield Request(url='https://voh.com.vn'+u[:-5]+"-p1.html",callback=self.parse1,meta={"category1":c})

    def parse1(self,response):
        # print(response)
        arts=response.xpath("//div[@class='NewsListItem_news-list-item-wrapper__15Cd1']")
        for i in arts:
            c2 = i.xpath("./div[@class='NewsListItem_news-list-item-ext__11cfJ']//a[1]/text()").extract()[0]
            u = i.xpath("./div[@class='NewsListItem_news-list-item-title__2a-Yt']//a[1]/@href").extract()[0]
            yield Request(url='https://voh.com.vn'+u,callback=self.parse2,meta={"category1":response.meta["category1"],"category2":c2})
        yield Request(url=response.url[:response.url.rfind("-p")+2]+str(response.meta["depth"]+1)+".html",callback=self.parse1,meta={"category1":response.meta["category1"]})

    def parse2(self, response):

        t = response.xpath(".//time/@datetime").extract()[0].strip()
        time0 = time.strptime(t[:19], "%Y-%m-%dT%H:%M:%S")
        time1 = time.mktime(time0)
        if OldDateUtil.time is None or int(time1) >= int(OldDateUtil.time):
            # print(response)
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.xpath("//h1[@class='style_html-tag-h1__23liH']/text()").extract()[0]
            item['category1'] = response.meta["category1"]
            item['category2'] = "" if response.meta["category2"]==response.meta["category1"] else response.meta["category2"]
            item['body'] = "".join(
                response.xpath("//div[contains(@class,'news-detail-content_detail-content__goYFs')]//p").xpath("string(.)").extract())
            item['abstract'] = "".join(response.xpath("//div[contains(@class,'news-detail-content_detail-intro__YTW8B')]").xpath("string(.)").extract())
            item['pub_time'] = time0
            item['images'] = response.xpath("//div[contains(@class,'news-detail-content_detail-content__goYFs')]//img/@src").extract()
            yield item
