import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

import re

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
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy


class DailymanaqibSpider(BaseSpider):
    author = '苏钰婷'
    name = 'dailymanaqib'  # name的重命名
    website_id = 2316
    language_id = 2238
    lan_num = 1
    start_urls = ['https://dailymanaqib.com/News-category/hot-news',
                  'https://dailymanaqib.com/News-category/pakistan-news',
                  'https://dailymanaqib.com/News-category/crime',
                  'https://dailymanaqib.com/News-category/sports-news',
                  'https://dailymanaqib.com/News-category/columns',
                  'https://dailymanaqib.com/News-category/international',
                  'https://dailymanaqib.com/News-category/national',
                  'https://dailymanaqib.com/News-category/business',
                  'https://dailymanaqib.com/News-category/showbiz'
                  ]

    def parse(self, response):
        articles = response.xpath('//div[@class="archive-post-grid col-lg-4 col-md-4 col-sm-8 col-xs-16"]')
        for article in articles:
            item = {}
            article_url = article.xpath('.//article/div/h4/a/@href').get()
            yield scrapy.Request(response.urljoin(article_url), callback=self.parse_article, meta={'item': item})

            # 查找是否存在分页链接
            next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
            if next_page:
                yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article(self, response):
        item = response.meta['item']
        # 提取标题
        title = response.xpath('//h1[@class="entry-title"]//text()').get()
        # 如果标题为空，则将其值设为 "None"
        item['title'] = title if title else "None"

        # 提取发布时间，并转换格式
        # 获取<time>标签中的日期时间字符串
        pub_date_str = response.xpath('normalize-space(//time[contains(@class,"updated")]/text())').extract_first()
        # May 5, 2022
        # 使用正则表达式把其中的月份、日期和年份放到三个分组中
        match = re.search(r'(\w+)\s+(\d+),\s+(\d+)', pub_date_str)
        if match:
            month_str, day_str, year_str = match.groups()
            # 填充月份和日期，使用EN_1866_DATE月份字典
            month_str = str(OldDateUtil.EN_1866_DATE.get(month_str, "")).zfill(2)
            day_str = str(day_str).zfill(2)
            # 格式化日期为"%Y-%m-%d 00:00:00"
            pub_time = f'{year_str}-{month_str}-{day_str} 00:00:00'
            # 时间截至
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            item['pub_time'] = pub_time

        # 提取分类
        item['category1'] = ''.join(response.xpath('//span[@class="cat-links"]//a/text()').getall())

        # 提取图片
        image_url = response.xpath('//div[@class="post-header-image"]/img/@src').extract_first()
        if image_url:
            item['images'] = [image_url]
        else:
            item['images'] = []

        # 提取正文，并去除空行
        body_paragraphs = response.xpath('//div[@class="entry-content"]//p/text()').getall()
        body_paragraphs = [para.strip() for para in body_paragraphs if para.strip() != '']
        item['body'] = '\n'.join(body_paragraphs)

        # 提取摘要
        first_sentence = body_paragraphs[0].split('.')[0] if '.' in body_paragraphs[0] else \
            body_paragraphs[0].split()[0]
        item['abstract'] = first_sentence

        # 如果正文只有一段，将正文和摘要拼接起来
        if len(body_paragraphs) == 1:
            item['body'] = item['body'] + '\n' + item['abstract']

        yield item