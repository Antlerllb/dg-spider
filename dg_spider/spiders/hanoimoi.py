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
import json

# 以下的头文件不要修改





#author:马嘉颖
# check：凌敏 pass
class HanoimoiSpider(BaseSpider):
    name = 'hanoimoi'
    website_id = 261  # 网站的id(必填)
    language_id = 2242  # 所用语言的id
    allowed_domains = ['hanoimoi.com.vn']
    start_urls = ['http://hanoimoi.com.vn/']


    def parse(self, response):
        catagory = response.xpath("//ul[@class='menufst nav']/li/a")
        for i in catagory[1:]:
            if i.xpath("./@href"):
                yield Request(url="http://hanoimoi.com.vn" + i.xpath("./@href").extract()[0], callback=self.parse1)
        pass

    def parse1(self,response):

        if response.xpath(".//input[@id='hdCategoryId']/@value"):
            id=response.xpath(".//input[@id='hdCategoryId']/@value").extract()[0]
            aid=response.xpath("//div[@class='lst-category']/input/@value").extract()[0]
            yield Request(url="http://hanoimoi.com.vn/Home/ArticleCategoryListMore?categoryId={}&day=&currentPage=1&lastArticleId={}".format(id,aid),
                          callback=self.parse2,
                      meta={"id":id,"aid":aid})

    def parse2(self, response):
        # print(response)
        datas = json.loads(response.body)['Content']
        page = re.findall(r'a href=[a-zA-Z0-9\']+/+[a-zA-Z0-9\'-]+/+[a-zA-Z0-9\'-]+/+[a-zA-Z0-9\'-]+/[a-zA-Z0-9\'-]+',datas)
        url1 = []

        for i in range(0, len(page)):
                new_url = re.findall(r'/[a-zA-Z0-9-]+/+[a-zA-Z0-9-]+/+[a-zA-Z0-9-]+/+[a-zA-Z0-9-]+', page[i])
                url1.append(new_url[0])

        # if response.xpath("//ul[@id='article-cate-more']/li"):
        #     articles = response.xpath("//ul[@id='article-cate-more']/li")
        #     for i in articles:
        #         t=i.xpath("./div[@class='period']/text()").extract()[0]
        #         new_t=t[1:6]+t[8:]
        #         time0 = time.strptime(new_t.strip(), "%H:%M %d/%m/%Y")
        #         time1 = time.mktime(time0)
        #         time2 = time.mktime(time.strptime(OldDateUtil.time, '%Y-%m-%d'))
        #     for i in range(0, len(page)):
                    # if int(time1) - int(time2) < 0:

        for i in url1:
            yield Request(url="http://hanoimoi.com.vn" + i,callback=self.parse3)
                    # yield Request(url="http://hanoimoi.com.vn" + i.xpath("./a[1]/@href").extract()[0],
                    #               callback=self.parse3,meta={"time":time0})
        yield Request(
                url="http://hanoimoi.com.vn/Home/ArticleCategoryListMore?categoryId={}&day=&currentPage={}&lastArticleId={}".format(response.meta['id'],response.meta['depth'],response.meta['aid']),
                callback=self.parse2, meta={"id":response.meta['id'],"aid":response.meta['aid']})


    def parse3(self, response):
        # print(response)
        t = response.xpath("//div[@class='definfo']/div[@class='period']/text()").extract()[0]
        new_t=t[1:6]+t[20:]
        try:
            time0 = time.strptime(new_t, "%H:%M %d/%m/%Y")
        except:

            time0 = time.localtime()
        time1 = time.mktime(time0)
        if OldDateUtil.time is None or int(time1) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            if len(response.xpath("//h1[@class='caption']/text()").extract())!=0:
                item['title'] = response.xpath("//h1[@class='caption']/text()").extract()[0]
                try:
                    item['category1'] = response.xpath("//div[@class='breadcrum']/a[2]/text()").extract()[0]
                except:
                    item['category1']=''
                try:
                    item['category2'] = response.xpath("//div[@class='breadcrum']/a[3]/text()").extract()[0]
                except:
                    item['category2'] =''
                item['body'] = "".join(
                        response.xpath("//div[@class='article']/p/following-sibling::p").xpath("string(.)").extract())
                if len(response.xpath("//div[@class='article']/p[1]/strong/text()").extract())!=0:
                    item['abstract'] = response.xpath("//div[@class='article']/p[1]/strong/text()").extract()[0].strip()
                item['pub_time'] =time0
                item['images'] = response.xpath("//div[@class='thumbox']/img/@src").extract()
                yield item
