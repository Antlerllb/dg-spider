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
# check：凌敏 pass 注意不需要打印response
class BaoquocteSpider(BaseSpider):
    name = 'baoquocte'
    website_id = 280  # 网站的id(必填)
    language_id = 2242  # 所用语言的id
    # allowed_domains = ['baoquocte.com']
    start_urls = ['https://baoquocte.vn/']


    def parse(self, response):
        lis=response.xpath("//ul[@class='main-menu']/li/a/@href").extract()
        for i in lis[1:]:
            yield Request(url=i,callback=self.parse1,headers={'Referer': 'https://baoquocte.vn/'})

    def parse1(self, response):
        # print(response)
        articles = response.xpath("//div[@class='bx-listing fw lt mb clearfix']/div[@class='article']")
        for i in articles:
           if(i.xpath("./a[1]/@href")):
                yield Request(url=i.xpath("./a[1]/@href").extract()[0], callback=self.parse2)
        if response.xpath("//div[@class='__MB_ARTICLE_PAGING fw lt mb clearfix']/div[@class='rt']/a/@href"):
            yield Request(url=response.xpath("//div[@class='__MB_ARTICLE_PAGING fw lt mb clearfix']/div[@class='rt']/a/@href").extract()[-1],
                          callback=self.parse1,
                          headers={'Referer': 'https://baoquocte.vn/'})

    def parse2(self,response):
        time0 = time.strptime(response.xpath("//span[@class='format_time']/text()").extract()[0],
                              "%d/%m/%Y %H:%M")
        time1 = time.mktime(time0)
        if OldDateUtil.time is None or int(time1) >= int(OldDateUtil.time):
            list1=response.xpath("//h1[@class='article-detail-title f0']/text()").extract()
            if len(list1)!=0:
                item = NewsItem(language_id=self.language_id)
                item['title'] = response.xpath("//h1[@class='article-detail-title f0']/text()").extract()[0].strip()
                item['category1'] =response.xpath("//li[@class='menu-alias']/a/text()").extract()[0]
                item['category2']=''
                item['body'] = "".join(response.xpath("//div[@id='__MB_MASTERCMS_EL_3']/p").xpath("string(.)").extract())
                item['abstract'] = response.xpath("//div[@class='article-detail-desc fw lt f0 mb clearfix']/text()").extract()[0].strip()
                item['pub_time'] = time0
                item['images'] = response.xpath("//table[@class='MASTERCMS_TPL_TABLE']//img/@src").extract()
                yield item
        pass