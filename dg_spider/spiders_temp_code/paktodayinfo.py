import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

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


import json
from lxml import etree
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy


class PaktodayinfoSpider(BaseSpider):
    name = "paktodayinfo"
    author = '凌洪炜'
    website_id = 2291  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    allowed_domains = ["paktodayinfo.com"]
    start_urls = ["https://paktodayinfo.com/"]


    def convert_date(self,date_str):
        # 去除字符串两端的空格
        date_str = date_str.strip()
        # 解析日期字符串并转换为所需的格式
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
        formatted_date = date_obj.strftime('%Y-%m-%d 00:00:00')
        return formatted_date



    def parse(self, response):
        page_list = response.xpath('//div[@class="menu main-menu"]/ul/li/a')
        for index, column in enumerate(page_list):
            category1 = column.xpath('./text()').extract_first()
            url = column.xpath('./@href ').extract_first()
            if (index != 0):
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_get,
                    meta={'category1': category1}
                )

    def parse_get(self, response):

        category1 = response.meta['category1']
        news_list = response.xpath('//div[@class="content-area"]//article//h3')
        if news_list is not None and news_list != '':
            for news in news_list:
                url = news.xpath('./a/@href').extract_first()


                pub_time = news.xpath('./..//span[@class="item-metadata posts-date"]//a/text()').extract_first()
                pub_time = self.convert_date(pub_time) #将爬取的时间格式改成类似2024-12-22 00:00:00这种格式


                if OldDateUtil.time     is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                    continue
                else:
                    item = {}
                    # item['images'] = news.xpath('./../..//a/img/@src').extract_first()
                    item['category1'] = category1
                    item['title'] = news.xpath('./a/text()').extract_first() #.replace('\xa0', ' ')
                    item['pub_time'] = pub_time
                    item['abstract'] = news.xpath('./..//div[@class="post-description"]/p/text()').extract_first().replace('\xa0', ' ')
                    # print('url:', url, 'item', item)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_item,
                        meta={'item': item}
                    )

        # 翻页按钮：>
        next_url = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        # 判断终止条件
        if next_url is not None and next_url != '':
            # 最后一页为：javascript:void(0)
            # 符合条件不停地翻页
            # next_url = response.urljoin(part_url)
            # 构建请求对象并且返回给引擎
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_get,
                meta={'category1': category1}
            )

    def parse_item(self, response):
        item = NewsItem(response.meta['item'])
        article = response.xpath('//div[@class="entry-content"]//text()').extract()

        if len(article) > 1:
            content = "\n".join(article)
        else:
            content = "\n" + item['abstract'] + "\n".join(article)

        item['body'] = content


        image = response.xpath('//div[@class="post-thumbnail full-width-image"]//@data-lazy-src').extract_first()
        # print('image:',image)
        if image == '' or image is None or image == 'NULL':
            item['images'] = []
        else:
            item['images'] = [image]

        item['language_id'] = 1866
        yield item