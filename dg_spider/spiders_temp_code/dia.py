import json
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




Spanish_2181_DATE = {'enero': '01',
                       'febrero': '02',
                       'marzo': '03',
                       'abril': '04',
                       'mayo': '05',
                       'junio': '06',
                       'julio': '07',
                       'agosto': '08',
                       'septiembre': '09',
                       'octubre': '10',
                       'noviembre': '11',
                       'diciembre': '12'}
#本网站无图片
#author:林泽佳
class DiaSpider(BaseSpider):
    name = 'dia'
    website_id = 2131  # 网站的id(必填)
    language_id = 2181  # 所用语言的id
    start_urls = ["https://diariodechimbote.com/"]
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2"}

    def parse(self, response):
        lis1 = ["editorial/", "noticias-locales", "opinion", "politica", "deportes"]
        url1 = [f'https://diariodechimbote.com/seccion/{type}' for type in lis1]
        for i in url1:
            yield Request(url=i, callback=self.parse2, headers={'Referer': 'https://www.diariodesevilla.es'})

    def parse2(self, response):
        list = response.xpath("//div[@class='davenport-post-image-wrapper']/a/@href").extract()
        for i in list:
            yield Request(url=i, callback=self.parse4,
                          headers={'Referer': 'https://www.diariodesevilla.es'})
        #翻页
        next_url = response.xpath("//a[@class='nextpostslink']/@href").extract_first()
        if next_url != '':
            yield Request(url=next_url, callback=self.parse2)
        else:
            self.logger.info("no more pages")

    def parse4(self, response):

        tm = response.xpath("//time[@class='entry-date published updated']/text()").extract()[0]#07/10/2022
        tmm = tm.split('/')
        time1 = "{}-{}-{} {}:{}:{}".format(tmm[2], tmm[1], tmm[0], "00", "00", "00") #年月日 %H:%M

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time1) >= OldDateUtil.time:
            item = NewsItem(language_id=self.language_id)
            title = response.xpath("//h1[@class='post-title entry-title']/text()").extract()[0].strip()
            pattern = re.compile(':',re.S)
            title = pattern.sub('',title).strip()
            item['title'] = title


            item['category1'] =  response.xpath("//div[@class='post-categories']/a/text()").extract()[0]
            item['category2'] = ''

            item['body'] = "".join(response.xpath("//div[@class='entry-content']/p/text()").extract())

            item['abstract'] = response.xpath("//div[@class='entry-content']/p/text()").extract_first()
            item['pub_time'] = time1
            item['images'] = []
            yield item
        else:
            self.logger.info("时间截止")
