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
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# 以下的头文件不要修改




#author:马嘉颖
# check：凌敏 pass
class SohaSpider(BaseSpider):
    name = 'soha'
    website_id = 255  # 网站的id(必填)
    language_id = 2242  # 所用语言的id
    allowed_domains = ['soha.vn']
    start_urls = ['https://soha.vn/']


    def parse(self, response):
        category = response.xpath("//div[@class='inner clearfix']/a")
        for i in category[1:-1]:
            yield Request(url="https://soha.vn" + i.xpath("./@href").extract()[0],
                          callback=self.parse11,
                          meta={"category1":i.xpath("./text()").extract()[0]})
        pass


    def parse11(self, response):
        category1 = response.xpath("//div[@class='kbws-list']//li//a")
        yield Request(url="https://soha.vn/timelinenew/"+response.xpath("//div[@class='aspNetHidden']/input[1]/@value").extract()[0]+"/trang-1.htm",
                      callback=self.parse2,
                      meta={"category1":response.meta["category1"],"category2":""})
        for i in category1[1:]:
            yield Request(url="https://soha.vn" + i.xpath("./@href").extract()[0],
                          callback=self.parse1,
                          meta={"category1":response.meta["category1"],"category2":i.xpath("./text()").extract()[0]})

    def parse1(self,response):
        # print(response)
        value=response.xpath("//div[@class='aspNetHidden']/input[1]/@value").extract()[0]
        yield Request(url="https://soha.vn/timelinenew/"+value+"/trang-1.htm",
                      callback=self.parse2,
                      meta={"category1":response.meta["category1"],"category2":response.meta["category2"]})

    def parse2(self, response):
        # print(response)
        if response.xpath("//li"):
            articles = response.xpath("//li")
            for i in articles:
                j=i.xpath("./div/a/@href").extract()[0]
                if(j[0:10]!='/big-story'):
                    yield Request(url="https://soha.vn" + j,
                                  callback=self.parse3,
                                  meta={"category1":response.meta["category1"],"category2":response.meta["category2"]})
            yield Request(url=response.url[:response.url.find("trang-")+6]+str(response.meta["depth"])+".htm",
                          callback=self.parse2,
                          meta={"category1":response.meta["category1"],"category2":response.meta["category2"]})
        else:
            return

    def parse3(self,response):
        # print(response)
        t = response.xpath("//*[@class='news-info']/time/text()").extract()[0]
        try:
            t = t[0:16]
            time0 = time.strptime(t.strip(), "%d/%m/%Y %H:%M")
        except:
            time0=time.localtime()
        time1 = time.mktime(time0)
        if OldDateUtil.time is None or int(time1) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['title']=response.xpath("//h1[@class='news-title']/text()").extract()[0].strip()
            item['category1'] = response.meta["category1"]
            item['category2']=response.meta["category2"]
            item['body'] = "".join(response.xpath("//div[@class='clearfix news-content']/p").xpath("string(.)").extract()).strip()
            item['abstract'] = "".join(response.xpath("//h2[@class='news-sapo']").xpath("string(.)").extract()).strip()
            item['pub_time'] = time0
            item['images'] = response.xpath("//div[@type='Photo']//img/@src").extract()
            yield item
