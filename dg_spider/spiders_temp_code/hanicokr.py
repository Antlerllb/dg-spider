import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


import json
import re
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



class HanicokrSpider(BaseSpider):  # 类名重命名
    author = '付鹏飞'
    name = 'hanicokr'  # name的重命名
    website_id = 902  # id一定要填对！
    language_id = 1991  # id一定要填对！
    start_urls = ['https://www.hani.co.kr/arti/politics',
                  'https://www.hani.co.kr/arti/society',
                  'https://www.hani.co.kr/arti/area',
                  'https://www.hani.co.kr/arti/economy',
                  'https://www.hani.co.kr/arti/international',
                  'https://www.hani.co.kr/arti/science',]
    lan_num =4

    def __init__(self, *args, **kwargs):
        super(HanicokrSpider, self).__init__(*args, **kwargs)
        self.page = 2  # 初始化为第一页



    def parse(self, response):  #主页，用于点进各个新闻(一级分类)
        list = response.xpath('//*[@id="__next"]/div/div/div[2]/div[3]/div[1]/div/ul/li')
        for i in list:
            class_url = 'https://www.hani.co.kr' + i.xpath('./article/a/@href').extract_first()
            pub_time = i.xpath('./article/a/div[1]/div[2]/div/text()').extract_first() + ':00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            response.meta['pub_time'] = pub_time
            yield scrapy.Request(url=class_url, callback=self.parse_item, meta=response.meta)
        # 翻页
        next_page_url = response.xpath('/html/head/meta[9]/@content').extract_first() + '?page={}'.format(self.page)
        if next_page_url is not None:
            yield scrapy.Request(url=next_page_url, callback=self.parse, meta=response.meta)
        self.page += 1  # 增加页数

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.xpath('/html/head/title/text()').extract()
        abstract = response.xpath('/html/head/meta[@name="description"]/@content').extract()

        block = BeautifulSoup(response.text, 'html.parser')
        script_tag = block.find('script', id='__NEXT_DATA__')
        json_str = script_tag.string
        # 将JSON字符串转换为Python字典
        data = json.loads(json_str)
        # 提取并清洗文章正文内容
        content = data['props']['pageProps']['article']['content']
        # 清洗HTML标签
        clean_content = BeautifulSoup(content, 'html.parser').get_text()
        # 清除多余字符串
        clean_content = re.sub(r'\[%%IMAGE\d+%%\]', '', clean_content)
        body=clean_content
        if body is not None:
            # 将正文按段落分隔
            body_paragraphs = body.split('. ')
            body = body.replace(' ', '')
            body = body.replace('.', '\n')
            # 检查是否只有一段，如果只有一段，将摘要和正文拼接起来
            if len(body_paragraphs) == 1:
                body = abstract + '\n' + body

        category1 = data['props']['pageProps']['article'][ "section"]["label"]

        image = []
        imglist = data['props']['pageProps']['article']['imageList']
        for i in imglist:
            if i is not None:
                image.append(imglist[0]["url"])

        item['title'] = title
        item['category1'] = category1
        item['pub_time'] = response.meta['pub_time']
        item['abstract'] = abstract
        item['body'] = ' '
        item['body'] = body
        item['images'] = image
        if body != '':
            yield item

















