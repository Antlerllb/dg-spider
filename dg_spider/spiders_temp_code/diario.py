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





#个别网站才有图片，有些网站没有内容
#author:林泽佳
# check:czy
class DiarioSpider(BaseSpider):
    name = 'diario'
    website_id = 1334  # 网站的id(必填)
    language_id = 2181  # 所用语言的id
    # allowed_domains = ['diarioelsoldecusco.com']
    start_urls = ['http://www.diarioelsoldecusco.com/']
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2"}
    # proxy = "02"

    def parse(self, response):
        articles = response.xpath("//main[@class='col-md-9 col-sm-8 content-left']/article/header/h2/a/@href").extract()
        for i in articles:
            yield Request(url=i, callback=self.parse2, headers={'Referer': 'http://www.diarioelsoldecusco.com/'})
        #翻页
        urls = response.xpath("//a[@class='next page-numbers']/@href").extract()
        for i in urls:
            if i != '':
                yield Request(url=i,callback=self.parse,headers={'Referer': 'http://www.diarioelsoldecusco.com/'})
            else:
                self.logger.info("no more pages")

    def parse2(self, response):

        tm = response.xpath("//span[@class='posted-on']/a/time/@datetime").extract()[0]#2022-10-06T13:25:42+00:00
        pattern = re.compile(r'T', re.S)
        time_list = pattern.sub(' ', tm)
        tmm = time_list.split(' ')#2022-10-06 13:25:42+00:00

        min_sec = tmm[1].split(':')#13 25 42+00 00
        time1 = tmm[0] + " {}:{}:{}".format(min_sec[0], min_sec[1], "00")# %d/%m/%Y %H:%M

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time1) >= OldDateUtil.time:
            #list1 = response.xpath("//h1[@class='content-title']/text()").extract()
            # if len(list1)!=0:
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.xpath("//a[@rel='bookmark']/text()").extract()[0].strip()

            item['category1'] = 'ELSOL'
            item['category2'] = ''

            body = "".join(response.xpath("//div[@class='post-content']/p/text()").extract())
            item['body'] = body

            item['abstract'] = response.xpath("//div[@class='post-content']/p/text()").extract()[0].strip()
            item['pub_time'] = time1
            item['images'] = response.xpath("//figure[@class='thumbnail']//img/@src").extract()
            yield item
        else:
            self.logger.info("时间截止")
