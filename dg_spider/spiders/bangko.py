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
import json
from scrapy.http import Request, Response
import re
import scrapy
import time
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

# 以下的头文件不要修改




Thai_2208_DATE_ABB = {'ม.ร.': '01',
                  'ก.พ.': '02',
                  'มี.ค.': '03',
                  'เม.ย.': '04',
                  'พ.ค.': '05',
                  'มิ.ย.': '06',
                  'ก.ค.': '07',
                  'ส.ค.': '08',
                  'ก.ย.': '09',
                  'ต.ค.': '10',
                  'พ.ย.': '11',
                  'ธ.ค.': '12'}
#author:林泽佳
class BangkoSpider(BaseSpider):
    name = 'bangko'
    website_id = 1666  # 网站的id(必填)
    language_id = 2208  # 所用语言的id
    # allowed_domains = ['bangkokbiznews.com/']
    # start_urls = ['https://www.bangkokbiznews.com/']
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2"}

    type_list = ["news", "politics", "business", "finance", "realestate", "auto", "tech", "health", "world",
                 "lifestyle", "biz2u"]
    start_urls = [f'https://api.bangkokbiznews.com/api/v1.0/categories/{type}?page={i}' for type in type_list for i in range(1, 220)]
    #proxy = "02"

    def start_requests(self): # post请求
        for url in self.start_urls:
            yield scrapy.FormRequest(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        soup = json.loads(response.text)['data']
        for i in soup:
            list = i['link']
            url = "https://www.bangkokbiznews.com/" + list
            yield Request(url=url, callback=self.parse2)

    def parse2(self,response):

        tm = response.xpath("//span[@class='date']/text()").extract()[0]
        time_list = tm.split(' ')

        #12 ก.ย. 2565 เวลา 7:09 น.
        min_sec = time_list[4].split(':')

        time1 = "{}-{}-{} {}:{}:{}".format(int(time_list[2])-543, Thai_2208_DATE_ABB[time_list[1]], time_list[0],min_sec[0],
                                          min_sec[1], "00")#%d/%m/%Y %H:%Mtime_list[-2]

        # time0 = time.strptime(response.xpath("//span[@class='date']/text()").extract()[0],
        #                       "%d/%m/%Y %H:%M")
        # time1 = time.mktime(time0)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time1) >= OldDateUtil.time:
            list1=response.xpath("//h1[@class='content-title']/text()").extract()
            # if len(list1)!=0:
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.xpath("//h1[@class='content-title']/text()").extract()[0].strip()
            item['category1'] =response.xpath("//a[@class='content-category']/text()").extract()[0]
            item['category2']=''

            body_part = "".join(response.xpath("//div[@id='content']//p/text()").extract())
            pattern = re.compile(r'\s|\n|<p>|</p>|<span>|</span>|<strong>|</strong>', re.S)
            content_list = pattern.sub('', body_part)
            item['body'] = content_list

            item['abstract'] = response.xpath("//h2[@class='content-blurb']/blockquote/text()").extract()[0].strip()
            item['pub_time'] = time1
            item['images'] = response.xpath("//div[@class='content-feature-image']//img/@src").extract()
            yield item
        else:
            self.logger.info("时间截止")
