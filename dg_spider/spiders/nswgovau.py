from copy import deepcopy
import re
import parsel
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

import scrapy
import requests

from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
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
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import requests     # 请求模块
import parsel       # 解析数据模块
month_spe = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }
# check：林泽佳
# pass
# 刘宇康 寒假3
class NswgovauSpider(BaseSpider):
    name = 'nswgovau'
    # allowed_domains = ['education.nsw.gov.au']
    # https://education.nsw.gov.au/teach-nsw/news-and-events/news.all.all.1.undefined
    start_urls = ['https://education.nsw.gov.au/teach-nsw/news-and-events/news.all.all.1.undefined', 'https://education.nsw.gov.au/news.all.all.1.html#catalogue_auto']
    website_id = 2195
    language_id = 1866

    def parse(self, response):
        flag = True
        divs = response.xpath('//div[@class="col-sm-12 col-md-6 col-lg-4 d-flex"]')
        if OldDateUtil.time is not None:
            raw_time = divs[0].css('div.card-body time::text').get() + ' 00:00:00'
            month = re.findall(r'\w+', raw_time)[1]
            raw_time = raw_time.replace(month, month_spe[month])
            last_time = time.strftime('%Y-%m-%d 00:00:00', time.strptime(raw_time, '%d %m %Y 00:00:00'))
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for div in divs:
                link = 'https://education.nsw.gov.au/'+div.css('a::attr(href)').get()
                title = div.css('h4.card-title::text').get()
                abstract = div.css('div.card-body p::text').get()
                raw_time = div.css('div.card-body time::text').get()+' 00:00:00'
                month = re.findall(r'\w+', raw_time)[1]
                raw_time = raw_time.replace(month, month_spe[month])
                pub_time = time.strftime('%Y-%m-%d 00:00:00', time.strptime(raw_time, '%d %m %Y 00:00:00'))
                # 都是news
                if len(response.url) > len('https://education.nsw.gov.au/news.all.all.1.html#catalogue_auto'):
                    meta = {
                        'title': title,
                        'abstract': abstract,
                        'pub_time': pub_time,
                        'category1': 'Teach NSW',
                        'category2': 'News'
                    }
                else:
                    meta = {
                        'title': title,
                        'abstract': abstract,
                        'pub_time': pub_time,
                        'category1': 'Home',
                        'category2': 'News'
                    }
                yield Request(url=link, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if response.xpath('//a[@title="Next page"]/span/text()').get() == "Next":
                num = int(re.findall(r'\d+', response.url)[0]) + 1
                next_page = response.url.replace(re.findall(r'\d+', response.url)[0], str(num))
                print(next_page)
                yield Request(url=next_page, callback=self.parse)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = response.xpath('//div[@class="cmp-text"]').xpath('string(.)').get()
        if response.xpath('//img[@class="img-mobile-rendition"]/@src').get():
            item['images'] = ['https://education.nsw.gov.au'+response.xpath('//img[@class="img-mobile-rendition"]/@src').get()]
        else:
            # 视频存不了
            item['images'] = []
        yield item


