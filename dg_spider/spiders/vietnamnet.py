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




#author:陈麒亦
# check：凌敏 pass
class vietnamnetSpider(BaseSpider):
    name = 'vietnamnet'
    website_id = 247  # 网站的id(必填)
    language_id = 2242 # 所用语言的id
    start_urls = ['https://vietnamnet.vn/']
    allowed_domains = ['vietnamnet.vn']


    def parse(self,response):
        catagory=response.xpath("//ul[@class='menu']/li")

        for i in catagory[1:-2]:
            if i.xpath("./a/@href"):
                yield Request(url="https://vietnamnet.vn"+i.xpath("./a/@href").extract()[0]+"-page0",callback=self.parse2)
        pass

    def parse2(self,response):
        # print(response)
        if response.xpath("//div[@class='feature-box']"):
            articles=response.xpath("//div[@class='feature-box']")
            for i in articles:
                yield Request(url="https://vietnamnet.vn"+i.xpath(".//a[1]/@href").extract()[0],callback=self.parse3)
            yield Request(url=response.url[:response.url.find("-page")+5]+str(response.meta['depth']),callback=self.parse2)
        else:
            return


    def parse3(self,response):
        try:
            time0 = time.strptime(response.xpath(".//div[@class='breadcrumb-box__time']//span/text()").extract()[0].strip(), "%d/%m/%Y   %H:%M (GMT+07:00)")
        except:
            time0 = time.localtime()
        time1 = time.mktime(time0)
        if OldDateUtil.time is None or int(time1) >= int(OldDateUtil.time):
            # print(response)
            item = NewsItem(language_id=self.language_id)
            if(response.xpath("//h1/text()")):
                item['title']=response.xpath("//h1/text()").extract()[0]
            if(response.xpath("//div[@class='breadcrumb-box__link ']")):
                item['category1'] = response.xpath("//div[@class='breadcrumb-box__link ']//a[1]/text()").extract()[0].strip()
            if(response.xpath("//div[@class='breadcrumb-box__link ']//a[2]")):
                item['category2'] = response.xpath("//div[@class='breadcrumb-box__link ']//a[2]/text()").extract()[0].strip()
            item['body'] = "".join(response.xpath("//div[contains(@class,'maincontent')]//p").xpath("string(.)").extract()).strip()
            if(response.xpath("//div[@class='newFeature__main-textBold']")):
                item['abstract'] = "".join(response.xpath("//div[@class='newFeature__main-textBold']").xpath("string(.)").extract()).strip()
            item['pub_time'] = time0
            item['images'] = response.xpath("//div[@class='maincontent ']//img/@src").extract()
            yield item