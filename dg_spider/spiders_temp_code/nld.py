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
# check：凌敏 pass
class NldSpider(BaseSpider):
    name = 'nld'
    website_id = 263  # 网站的id(必填)
    language_id = 2242  # 所用语言的id
    allowed_domains = ['nld.com.vn']
    start_urls = ['https://nld.com.vn/']

    def parse(self, response):
        category = response.xpath("//div[@class='menu-container']//ul[@class='menu-top clearfix']/li")
        for i in category[1:-3]:
            if i.xpath("./a/@href"):
                yield Request(url="https://nld.com.vn" + i.xpath("./a/@href").extract()[0], callback=self.parse11)
        pass


    def parse11(self, response):
        category = response.xpath("//ul[@class='sub-cate']/li")
        for i in category:
            if i.xpath("./a/@href"):
                yield Request(url="https://nld.com.vn" + i.xpath("./a/@href").extract()[0], callback=self.parse1)
        pass


    def parse1(self,response):
        value=response.xpath("//div[@class='aspNetHidden']/input[3]/@value").extract()[0]
        yield Request(url="https://nld.com.vn/loadmorecategory-"+value+"-1.htm",callback=self.parse2)

    def parse2(self, response):
        # print(response)
        if response.xpath("//div[@class='cate-list-news mg_t10']/ul[@class='list-news clearfix']/li"):
            articles = response.xpath("//div[@class='cate-list-news mg_t10']/ul[@class='list-news clearfix']/li")
            for i in articles:
                if(i.xpath("./a/@href")):
                    yield Request(url="https://nld.com.vn" + i.xpath("./a/@href").extract()[0],
                                  callback=self.parse3)
            yield Request(url=response.url[:response.url.rfind("-")+1]+str(response.meta["depth"]+1)+".htm", callback=self.parse2)
        else:
            return

    def parse3(self,response):
        t=response.xpath("//p[@class='dateandcat clearfix']/span[@class='pdate fl']/text()").extract()[0]
        t=t[0:11]+t[-5:]

        time0 = time.strptime(t,"%d-%m-%Y %H:%M")
        time1 = time.mktime(time0)
        if OldDateUtil.time is None or int(time1) >= int(OldDateUtil.time):

            item = NewsItem(language_id=self.language_id)
            item['title']=response.xpath("//h1[@class='title-content']/text()").extract()[0].strip()
            item['category1'] = response.xpath("//p[@class='dateandcat clearfix']/a/text()").extract()[0].strip()
            item['category2']=''
            item['body'] = "".join(response.xpath("//div[@class='content-news-detail old-news']/p").xpath("string(.)").extract())
            item['abstract'] = response.xpath("//h2[@class='sapo-detail']/text()").extract()[0].strip()
            item['pub_time'] = time0
            item['images'] = response.xpath("//div[@class='VCSortableInPreviewMode active']//img/@src").extract()
            yield item

