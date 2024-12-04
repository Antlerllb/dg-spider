# -*- coding: utf-8 -*-

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
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re



class AkpgovSpider(BaseSpider):
    name = "akpgov"
    website_id = 2698
    language_id = 2275
    author = '陈彧'
    start_urls = ["https://www.akp.gov.kh/kh"]
    i = 1

    def __init__(self, *args, **kwargs):
        super(AkpgovSpider, self).__init__(*args, **kwargs)
        self.page = 2  # 初始化为第一页

    @staticmethod
    def gain_detail_time(fault_time):
        i = int(fault_time.split(':')[0])
        if i == 24:
            i = 0
        detail_time = str(i).zfill(2) + ':' + fault_time.split(':')[1].zfill(2) + ':00'
        return detail_time

    @staticmethod
    def time_fix(time_list):
        month = str(time_list[0].split(".")[1]).zfill(2)
        formatted_time = f'{time_list[0].replace(".", "-")} {time_list[1]}'
        return str(formatted_time)

    def parse(self, response):
        block = response.xpath(
            '/html/body/div[1]/div[3]/div/div/div[1]/div[@class="single-blog-post small-featured-post    shadow-sm p-3  bg-light rounded"]')
        # print(len(block))
        if block is not None:
            for i in block:
                title = i.xpath('./div[1]/a/text()').extract_first()
                # print(title)
                # 获取当前新闻的具体网址
                detail_url = i.xpath('./div[1]/a/@href').extract_first()
                # print(detail_url)
                # 获取新闻的摘要
                # /html/body/div[1]/div[3]/div/div/div[1]/div/div[2]/div[2]/a/h6
                abstract = i.xpath('./div[2]/div[2]/a/h6/text()').extract_first()
                # print(abstract)
                if not abstract:
                    abstract = "abstract is none"  # 如果摘要为空，则设为空字符串
                # 初使页面上的图片无法获取
                # images = []
                # 用image里的信息去获取时间
                image = i.xpath('.//div[2]/div[1]/a/img/@src').extract_first()
                if image is not None:
                    # 使用正则表达式匹配日期模式,目标：2023-12-12 20:01:00
                    pattern = r'\d{4}[/-]\d{2}[/-]\d{2}'
                    match = re.search(pattern, image)
                    # 提取日期
                    if match:
                        pub_time = match.group()
                    pub_time = pub_time.replace('/', '-')
                    # 添加时间部分，假设使用00:00:00
                    pub_time += ' 00:00:00'
                    if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                        return
                    # 将获取的信息通过response的meta传递到下一个函数
                    response.meta['pub_time'] = pub_time
                    response.meta['title'] = title
                    response.meta['abstract'] = abstract
                    yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta,
                                         headers={'Referer': detail_url})
        else:
            return

        # 翻页逻辑
        next_page_url = f'https://www.akp.gov.kh/kh?page={self.page}'
        yield scrapy.Request(next_page_url, callback=self.parse, meta=response.meta)
        self.page += 1  # 增加页数

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        category1 = 'NATIONAL NEWS'
        title = response.meta['title']
        abstract = response.meta['abstract']
        # 获取每个新闻的图片
        images = []
        image = response.xpath('/html/body/div[1]/div/div/div[1]/div/div/div/div/div[2]/div/p/img/@src').extract_first()
        image = 'https://img0.baidu.com/it/u=3137336022,1949303833&fm=253&fmt=auto&app=138&f=JPEG?w=422&h=436'
        if image is not None:
            images.append(image)
        body = response.xpath('/html/body/div[1]/div/div/div[1]/div/div/div/div/div[2]/div/p/text()').extract()
        if body is not None:
            body = '\n'.join(filter(lambda x: x.strip() != '' and x != '\xa0', body))
            # 将正文按段落分隔
            body_paragraphs = body.split('\n')
            # 检查是否只有一段，如果只有一段，将摘要和正文拼接起来
            if len(body_paragraphs) == 1:
                body = abstract + '\n' + body
            else:
                body = '\n'.join(body_paragraphs)
            item['title'] = title
            item['abstract'] = abstract
            item['body'] = body
            item['category1'] = category1
            item['images'] = images
            item['pub_time'] = response.meta['pub_time']
        if body != '':
            yield item
            # print(f"第【{self.i}】个网站抓取成功->{response.request.url}")
            # print(item['body'])
            self.i = self.i + 1
