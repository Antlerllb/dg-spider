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




#author:庄靖哲
# check: 凌敏 pass
class ZhVietnamplusSpider(BaseSpider):
    name = 'zh.vietnamplus'
    allowed_domains = ['zh.vietnamplus.vn']
    start_urls = ['https://zh.vietnamplus.vn/api/menu.html']
    website_id = 243  # 网站的id(必填)
    language_id = 1813  # 所用语言的id


    # 主页内容
    def parse(self, response):
        pro = response.xpath('//ul[@class="site-menu"]/li/a')[1:9]
        for page1 in pro:
            yield Request(url="https://zh.vietnamplus.vn" + page1.xpath('.//@href').get(),callback=self.parse1,meta={'category1': page1.xpath('./text()').get()})
        pass

    def parse1(self, response):
        pro = response.xpath("//article[@class='story']/h2/a/@href").getall()
        if pro:
            for i in pro:
                yield Request(url="https://zh.vietnamplus.vn" +i,
                                 callback=self.parse2,
                                meta={'category1':response.meta['category1']})
        next=response.xpath('//*[@id="ctl00_mainContent_ContentList1_pager"]/ul/li//@href').getall()[:-1]
        for x in next:
            yield Request(url="https://zh.vietnamplus.vn"+x,callback=self.parse1,meta={'category1':response.meta['category1']})

    def parse2(self, response):
        # print(response)#.//div[@class='source']//@datetime
        time0 = time.strptime(response.xpath("//div[@class='source']/time/@datetime").get(),
                              "%Y-%m-%d %H:%M")
        time1 = time.mktime(time0)
        # time2 = time.mktime(time.strptime(OldDateUtil.time, '%Y-%m-%d'))
        # if int(time1) - int(time2) < 0:
        if not OldDateUtil.time or int(time1) >= int(OldDateUtil.time) and response.xpath('//div[@class="content article-body cms-body AdAsia"]'):
            item = NewsItem(language_id=self.language_id)
            response.xpath('//h1[@class="details__headline cms-title"]/text()').get().strip()
            item['category1'] = response.meta['category1']
            # ca1=response.xpath("//div[@class='action-link']/div[@class='date']/h4/a/strong/text()").extract()[0].strip()
            # if(item['category1']!=ca1):
            #
            #     item['category2'] = response.xpath("//div[@class='action-link']/div[@class='date']/h4/a/strong/text()").extract()[0].strip()
            # else:
            item['category2'] = response.xpath('//div[@class="topic"]/a/text()').get()
            item['title']=response.xpath('.//h1[@class="details__headline cms-title"]/text()').get()
            item['body'] = "".join(response.xpath('//div[@class="content article-body cms-body AdAsia"]').xpath(
                "string(.)").getall()).replace("\n", '').replace("\r", "")
            item['abstract'] = response.xpath("//div[@class='details__summary cms-desc']/text()").get().strip()
            item['pub_time'] = time0
            item['images'] = response.xpath("//div[@class='article-photo']//img/@src").getall()
            yield item
