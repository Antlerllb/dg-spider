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
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from lxml import etree


class DailypakistanSpider(BaseSpider):
    author = '苏钰婷'
    name = 'dailypakistan'  # name的重命名
    website_id = 2289
    language_id = 2238
    lan_num = 1
    start_urls = ['https://dailypakistan.com.pk/ajax_post_pagination']

    def parse(self, response):  # 解析初始网页
        post_per_page = 36  # 每页文章数量
        # 遍历生成文章的偏移量
        for offset in range(0, 2500, post_per_page):
            data = {
                'post_per_page': str(post_per_page),
                'post_listing_limit_offset': str(offset),
                'directory_name': 'categories_pages',
                'template_name': 'lazy_loading'
            }
            # 发送POST请求
            yield scrapy.FormRequest(url=response.url, formdata=data, callback=self.parse_articles)

    def parse_articles(self, response):  # 解析文章页面
        tree = etree.HTML(response.text)
        href = tree.xpath("//a/@href")
        for url in href:
            yield response.follow(url=url, callback=self.parse_article)

    def parse_article(self, response):
        item = {}
        # 提取标题
        item['title'] = response.xpath('//div[@class="title-area detail-title-area"]//h1/text()').get()

        # 提取发布时间
        pub_date_str = response.xpath('normalize-space(//div[@class="large-post-meta"]/span/text())').extract_first()
        # May 28, 2023
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
        item['category1'] = response.xpath('//div[@class="more-category"]//h3//a/text()').get()

        # 提取图片
        image_url = response.xpath(
                '//div[@class="responsive_test"]/div[@class="blur_image_background"]/@style').extract_first()
        if image_url:
            # 提取图片URL
            image_url = image_url.replace('background-image:url(', '').replace(');', '')
            item['images'] = [image_url]
        else:
            # 没有图片
            item['images'] = []

        # 提取正文，并去除空行
        body_paragraphs = response.xpath('//div[@class="news-detail-content-class"]//p/text()').getall()
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

