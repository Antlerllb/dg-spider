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





#这个网站的新闻有些有二级标签，有些没有二级标签
#有一些文章需要订阅才能查看，所以会出现一些list out of range的错误（只有需要订阅的新闻才会出现）
#author:林泽佳
# check: czy
# 网站有访问量的限制 达到最大访问量后会需要订阅
class lavozSpider(BaseSpider):
    name = 'lavoz'
    website_id = 1286  # 网站的id(必填)
    language_id = 2181  # 所用语言的id
    # allowed_domains = ['lavoz.com.ar']
    start_urls = ['https://www.lavoz.com.ar']
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2"}

    # proxy = "02"

    def parse(self, response):
        lis1 = ["lo-ultimo","ciudadanos","sucesos","politica","negocios","tendencias","numero-cero","mundo"]#无二级标签
        url1 = [f'https://www.lavoz.com.ar/{type}' for type in lis1]
        for i in url1:#直接进入解析标签
            yield Request(url=i, callback=self.parse2, headers={'Referer': 'https://www.lavoz.com.ar/'})

        lis2 = ["deportes", "vos", "agro"]  # 有二级标签
        url2 = [f'https://www.lavoz.com.ar/{type}' for type in lis2]
        for j in url2:#先跳到函数1分析子标签，再进入解析标签
            yield Request(url=j, callback=self.parse1, headers={'Referer': 'https://www.lavoz.com.ar/'})

    def parse1(self, response):#有二级标签的解析
        list = response.xpath(
            "//ul[@class='main-menu scrollable-menu flex justify-between list-reset menu-line m0 xs-hide sm-hide']/a/@href").extract()
        for i in list:
            yield Request(url="https://www.lavoz.com.ar" + i, callback=self.parse2,
                          headers={'Referer': 'https://www.lavoz.com.ar/'})

    def parse2(self, response):#无二级标签的解析对所有标签进行解析
        articles = response.xpath("//div[@class='article-image ']/a/@href").extract()
        for i in articles:
            if i != '':  # "/article/div/div[1]/a/@href")):
                yield Request(url="https://www.lavoz.com.ar/" + i,
                              callback=self.parse4)
        cate_list = response.url.split('/')
        cata1 = cate_list[3]
        url = [f'https://www.lavoz.com.ar/{cata1}/{i}' for i in range(1,300) ]
        for i in url:
            yield Request(url=i, callback=self.parse2, headers={'Referer': 'https://www.lavoz.com.ar/'})

    def parse4(self, response):

        tm = response.xpath("//span[@class='uppercase primary-color bold h6 time']/time/@datetime").extract()[0]
        pattern = re.compile(r'T', re.S)
        time_list = pattern.sub(' ', tm)
        tmm = time_list.split(' ')

        min_sec = tmm[1].split(':')
        time1 = tmm[0] + " {}:{}:{}".format(min_sec[0], min_sec[1], "00")# %d/%m/%Y %H:%M

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time1) >= OldDateUtil.time:
            #list1 = response.xpath("//h1[@class='content-title']/text()").extract()
            # if len(list1)!=0:
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.xpath("//h1[@class='h1 boldbold mb1 col-12 lg-col-9 md-col-8']/text()").extract()[0].strip()

            cate_list = response.url.split('/')
            cata1 = cate_list[3]
            if len(cate_list) > 6:
                cata2 = cate_list[4]
            else :
                cata2 = ''
            item['category1'] = cata1#response.xpath("//span[class='uppercase primary-color bold h6 ']/a/text()").extract()[0]
            item['category2'] = cata2#response.xpath("//span[class='uppercase primary-color bold h6 ']/text()").extract()[0]

            body = "".join(response.xpath("//div[@class='col col-12 pl1 mn0 body']/section/p/text()").extract())
            item['body'] = body

            item['abstract'] = response.xpath("//div[@class='story-subtitle']/p/text()").extract()[0].strip()
            item['pub_time'] = time1
            item['images'] = response.xpath("//div[@class='story-promo px2']//img/@src").extract()
            yield item
        else:
            self.logger.info("时间截止")
