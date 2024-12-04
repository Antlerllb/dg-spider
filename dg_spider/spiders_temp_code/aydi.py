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





#author:林泽佳
class AydiSpider(BaseSpider):
    name = 'aydi'
    website_id = 2336  # 网站的id(必填)
    language_id = 2227  # 所用语言的id
    start_urls = ['https://www.aydinlik.com.tr/']
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2"}


    def parse(self, response):
        lis1 = ["tum-haberler","yazarlar","ekonomi","dunya",]
        url1 = [f'https://www.aydinlik.com.tr/{type}' for type in lis1]
        for i in url1:#直接进入解析标签
            yield Request(url=i, callback=self.parse2, headers={'Referer': 'https://www.aydinlik.com.tr/'})

    def parse2(self, response):#无二级标签的解析对所有标签进行解析
        articles = response.xpath("//div[@class='col-12 col-lg']/a/@href").extract()
        for i in articles:
            if i != '':  # "/article/div/div[1]/a/@href")):
                yield Request(url=i, callback=self.parse4)
       #翻页
        next_url = response.xpath("//ul[@class='pagination mb-md']/li[last()]/a/@href").extract()
        if len(next_url)==0:
            self.logger.info("no more pages")
        else:
            for i in next_url:
                yield Request(url=i, callback=self.parse2)

    def parse4(self, response):

        tm = response.xpath("//div[@class='dates']/time/@datetime").extract_first()
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


            item['category1'] = response.xpath("//ol[@class='breadcrumb ']/li[last()]/a/text()").extract()
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
                img = response.xpath("//div[@class='post-detail-video-img']/figure/picture/img/@src").extract()
            except:
                img = response.xpath("//div[@class='gallery-item infinity-item ']/figure/picture/img/@src").extract()
            if img!='':
                item['images'] =img
            else:
                item['images'] = ''#有些是视频网站没有图片
            yield item
        else:
            self.logger.info("时间截止")
