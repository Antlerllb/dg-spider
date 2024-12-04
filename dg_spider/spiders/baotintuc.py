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
class BaotintucSpider(BaseSpider):
    name = 'baotintuc'
    website_id = 277  # 网站的id(必填)
    language_id = 2242  # 所用语言的id
    # allowed_domains = ['baotintuc.vn']
    start_urls = ['https://baotintuc.vn/']


    def parse(self, response):
        category=response.xpath("//div[@id='menu']//ul[@class='list-navbar']/li/a/@href").extract()
        ca=response.xpath("//ul[@class='list-navbar']/li/a/text()").extract()[0].strip()
        # print(category)
        for i in category[0:-2]:
            if "//" not in i:
                yield Request(url="https://baotintuc.vn"+i,callback=self.parse2,meta={"category1":ca})




    def parse2(self,response):
        # print(response)
        articles = response.xpath("//ul[@class='list-newsest']/li")
        for i in articles:
            if i.xpath("./a[1]/@href"):
                yield Request(url="https://baotintuc.vn"+i.xpath("./a[1]/@href").extract()[0],callback=self.parse3, meta={"category1": response.meta['category1']})
        if response.xpath("//ul[@class='list-pagination']/li/a[contains(@class,'active')]/../following-sibling::li[1]"):
            yield Request(url="https://baotintuc.vn"+response.xpath("//ul[@class='list-pagination']/li/a[contains(@class,'active')]/../following-sibling::li[1]/a/@href").extract()[0],callback=self.parse2,meta={"category1": response.meta['category1']})


    def parse3(self,response):
        # print(response)
        time0 = time.strptime(response.xpath("//div[@class='date']/span[@class='txt']/text()").extract()[0].strip()[-16:],"%d/%m/%Y %H:%M")
        time1 = time.mktime(time0)
        if OldDateUtil.time is None or int(time1) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.xpath("//div[@class='detail-content_wrapper']/div[@class='detail-left']/h1/text()").extract()[0].strip()
            item['category1'] =response.meta['category1']
            ca1=response.xpath("//div[@class='action-link']/div[@class='date']/h4/a/strong/text()").extract()[0].strip()
            if(item['category1']!=ca1):
                item['category2'] = response.xpath("//div[@class='action-link']/div[@class='date']/h4/a/strong/text()").extract()[0].strip()
            else:
                item['category2']=''
            item['body'] = "".join(response.xpath("//div[@class='contents']//p").xpath("string(.)").extract())
            item['abstract'] = response.xpath("//div[@class='content']/h2/text()").extract()[0].strip()
            item['pub_time'] = time0
            item['images'] = response.xpath("//div[@class='contents']//img/@src").extract()
            yield item

