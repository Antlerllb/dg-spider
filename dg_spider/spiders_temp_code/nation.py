import datetime
import json
import random
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from lxml import etree

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






class NationSpider(BaseSpider):
    name = "nation"  # name的重命名
    author = '谢彩云'
    website_id = 2312  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    allowed_domains = ["nation.com.pk"]
    start_urls = ["https://nation.com.pk/"]
    post_url = "https://www.nation.com.pk/ajax_post_pagination"
    proxy = '02'


    category_pll_offset = {
        "headlines": 9,
        "top-stories": 9,
        "national": 9,
        "sports": 18,
        "lifestyle-entertainment": 9,
        "business": 18,
        "international": 18,
        "editors-picks": 9,
        "snippets": 9,
        "lahore": 9,
        "karachi": 18,
        "islamabad": 18,

    }
    def parse(self, response):

        # 遍历字典并获取键和值
        for key, value in self.category_pll_offset.items():
            formdata = {
                "lang": "en_US",
                "post_per_page": "9",
                "post_listing_limit_offset": "9",
                'directory_name': "categories_pages",
                "template_name": "lazy_loading",
                "category_name": "sports",
            }
            formdata['post_listing_limit_offset'] = str(value)  # 请求页的初始post_listing_limit_offset
            formdata['category_name'] = str(key)  # 请求的栏目分类

            yield scrapy.FormRequest(
                url=self.post_url,
                formdata=formdata,
                meta={'key': key, 'post_listing_limit_offset': value, 'formdata': formdata},
                callback=self.parse_post
            )
        pass

    def parse_post(self, response):

        # post请求的解析方法
        key = response.meta['key']
        post_listing_limit_offset = response.meta['post_listing_limit_offset']
        formdata = response.meta['formdata']

        # 使用 lxml 库的 etree 解析 HTML
        tree = etree.HTML(response.text)

        # 遍历每篇文章
        for i in range(post_listing_limit_offset):
            if i < len(tree.xpath("//div[@class='jeg_meta_date']")):
                date_element = tree.xpath("//div[@class='jeg_meta_date']")[i]
                if date_element is not None:
                    date_text = date_element.text.strip()
                    # print("split之前的 date_text", date_text)

                    if '|' in date_text:
                        date_parts = date_text.split('|')
                        date_text = date_parts[1].strip()
                        # print("split之后的 date_text", date_text)

                    news_date = datetime.datetime.strptime(date_text, "%B %d, %Y")
                    pub_time = news_date.strftime("%Y-%m-%d 00:00:00")
                    # print(1111111)
                else:
                    pub_time = None
            else:
                break
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            else:
                item = {}
                item['category1'] = key
                # 获取新闻标题
                title_element = tree.xpath("///h3[@class='jeg_post_title']/a")[i]
                if title_element is not None:
                    item['title'] = title_element.text.strip()
                else:
                    item['title'] = ''

                item['pub_time'] = pub_time
                link = tree.xpath("//h3[@class='jeg_post_title']/a/@href")[i]

                # print(item)
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_item,
                    meta={'item': item}
                )
            post_listing_limit_offset = post_listing_limit_offset + 9
            formdata['post_listing_limit_offset'] = str(post_listing_limit_offset)

            # 继续发起下一页的 POST 请求
            yield scrapy.FormRequest(
                url=self.post_url,
                formdata=formdata,
                meta={'key': key, 'post_listing_limit_offset': post_listing_limit_offset, 'formdata': formdata},
                callback=self.parse_post,)

    def parse_item(self, response):
        time.sleep(random.uniform(0.5, 0.6))
        item = NewsItem(response.meta['item'])
        abstract_data = response.xpath('//*[@class="jeg_post_subtitle"]/text()').extract()
        # print("abstract_data: ", abstract_data)
        if abstract_data:
            item['abstract'] = abstract_data[0]
        else:
            item['abstract'] = 'null'
        article = response.xpath('//*[@class="content-inner news-detail-content-class"]/p/text()').extract()
        article_text = "\n".join(article)  # 将 article 中的每个段落连接成一个字符串

        content = "\n" + item['abstract'] + "\n" + article_text  # 连接字符串和文章内容
        item['body'] = content
        image = response.xpath('//*[@class="responsive_test"]/img/@src').extract_first()
        if image == '' or image is None or image == 'NULL':
            item['images'] = []
        else:
            item['images'] = [image]

        item['language_id'] = 1866
        # print(f'news item：{item} 66666')
        # print(666)
        yield item


