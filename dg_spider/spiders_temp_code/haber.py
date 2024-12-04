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





#有些网站没有图片
#author:林泽佳
class HaberSpider(BaseSpider):
    name = 'haber'
    website_id = 2343  # 网站的id(必填)
    language_id = 2227  # 所用语言的id
    start_urls = ['https://haberglobal.com.tr/']
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2"}


    def parse(self, response):
        lis1_url = response.xpath("//div[@class='category d-none d-lg-block']/a/@href").extract()
        for i in lis1_url:
            yield Request(url=i, callback=self.parse2, headers={'Referer': 'https://haberglobal.com.tr/'})

    def parse2(self, response):#对所有标签进行解析
        articles = response.xpath("//div[@class='post-item-row']/a/@href").extract()
        for i in articles:
            if i != '':  # "/article/div/div[1]/a/@href")):
                yield Request(url=i, callback=self.parse4)
       #翻页
        next_url = response.xpath("//ul[@class='pagination justify-content-center ']/li[last()]/a/@href").extract()
        if len(next_url)==0:
            self.logger.info("no more pages")
        else:
            for i in next_url:
                yield Request(url=i, callback=self.parse2)

    def parse4(self, response):

        tm = response.xpath("//time[@class='time']/@datetime").extract()[0]
        pattern = re.compile(r'T', re.S)
        time_list = pattern.sub(' ', tm)
        tmm = time_list.split(' ')

        min_sec = tmm[1].split('+')
        time1 = tmm[0] + " {}".format(min_sec[0])# 年月日 %H:%M

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time1) >= OldDateUtil.time:
            #list1 = response.xpath("//h1[@class='content-title']/text()").extract()
            # if len(list1)!=0:
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.xpath("//header[@class='post-detail-header']/h1/text()").extract()[0].strip()

            item['category1'] = response.xpath("//ol[@class='breadcrumb ']/li[2]/a/@title").extract()
            item['category2'] = ''

            body1 = "".join(response.xpath("//div[@class='content-text']").xpath('string(.)').extract())
            pattern = re.compile('\n',re.S)
            body = pattern.sub('',body1).strip()
            item['body'] = body
            try:
                abstract = response.xpath("//header[@class='post-detail-header']/h2/text()").extract()[0].strip()
            except:
                abstract = response.xpath("//div[@class='content-text']/p/text()").extract()[0].strip()#没有摘要选取文章第一段
            item['abstract'] =abstract
            item['pub_time'] = time1
            try:
                img = response.xpath("//div[@class='post-detail-video-img']/a/@href").extract()
            except:
                img = response.xpath("//div[@class='gallery-pagination-item']/a/@href").extract()
            if img == '':
                img = response.xpath("//div[@class='col-md-8 text-center']/a/@href").extract()
            if img!='':
                item['images'] =img
            yield item
        else:
            self.logger.info("时间截止")
