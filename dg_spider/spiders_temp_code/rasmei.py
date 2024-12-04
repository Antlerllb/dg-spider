#encoding: utf-8




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
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
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

class RasmeiSpider(BaseSpider):
    name = 'rasmei'
    author = '王伟任'
    website_id = 289
    language_id = 2275
    lan_num = 1

    start_urls = ['https://rasmeinews.com/?page=1']

    # 创建一个印尼语到英文的月份映射字典
    indonesian_to_english_month = {
        'Januari': 'January',
        'Februari': 'February',
        'Maret': 'March',
        'April': 'April',
        'Mei': 'May',
        'Juni': 'June',
        'Juli': 'July',
        'Agustus': 'August',
        'September': 'September',
        'Oktober': 'October',
        'November': 'November',
        'Desember': 'December'
    }

    # 优化的 parse_date 方法，无需 break
    def parse_date(self, time_pre):
        # 直接通过字典进行替换
        for indo_month, eng_month in self.indonesian_to_english_month.items():
            time_pre = time_pre.replace(indo_month, eng_month)
        # 转换日期格式
        date_obj = datetime.strptime(time_pre, "%d %B %Y")
        pub_time = date_obj.strftime("%Y-%m-%d 00:00:00")
        return pub_time

    def parse(self, response):
        for i in range(1,10):
            class_url= response.xpath('/html/body/div[1]/article/a/@href').extract()[i]
            time_pre = response.xpath('/html/body/div[1]/article/div[1]/div[2]/text()').extract()[i]
            # 使用 parse_date 方法转换日期
            pub_time = self.parse_date(time_pre)
            # print(pub_time)
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            # print(class_url)
            title = response.xpath('/html/body/div[1]/article/a/h2/text()').extract()[i]
            abstract = response.xpath('/html/body/div[1]/article/div[2]/p/text()').extract()[i]
            # # print(abstract)

            images =[]
            response.meta['images'] = images
            response.meta['pub_time'] = pub_time
            response.meta['title'] = title
            response.meta['abstract'] = abstract
            yield scrapy.Request(class_url, callback=self.parse_item, meta=response.meta)

        # next_url = response.xpath('//div[@id="next"]/a/@href').extract()
        # next_url ="https://rasmeinews.com/"+next_url
        # yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)

        for num_first in range(2,400):
            new_first_url = f'https://rasmeinews.com/?page={num_first}/'
            response.meta['class_url'] = new_first_url
            yield scrapy.Request(new_first_url, callback=self.parse, meta=response.meta)

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        category1 = "ភាសាខ្មែរ"
        abstract = response.meta['abstract']

        body = response.xpath('/html/body/div/div/div/p/text()').extract()

        if not body:
            body = ['ភាសាខ្មែរ']
        else:
            body = [re.sub(r'[\u00a0\u200b]+', '', text) for text in body]

        body = '\n'.join(body)
        if '\n' not in body:
            body = abstract + '\n' + body

        language_id = 1952

        item['language_id'] = language_id
        item['body'] = body
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['images'] = response.meta['images']
        item['category1'] = category1
        item['pub_time'] = response.meta['pub_time']


        yield item

