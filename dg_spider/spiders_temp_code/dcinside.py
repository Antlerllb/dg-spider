
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




class DcinsideSpider(BaseSpider):
    name = 'dcinside'
    website_id = 2028
    language_id = 1991
    author = '陈彧'
    start_urls = ['https://dcnewsj.joins.com/all/']
    i = 1

    def __init__(self, *args, **kwargs):
        super(DcinsideSpider, self).__init__(*args, **kwargs)
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
        block = response.xpath('/html/body/div[1]/div/div[4]/div[1]/div[2]/ul/li')
        if block is not None:
            for i in block:
                detail_time_list = i.xpath('./span[@class="byline"]/em/text()').extract_first().split(
                    " "
                )
                # 不用管太多，扔一个列表给他就可以了
                pub_time = datetime.strptime(DcinsideSpider.time_fix(detail_time_list), "%Y-%m-%d %H:%M")
                pub_time = pub_time.strftime("%Y-%m-%d %H:%M:%S")

                if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                    return
                # 获取当前新闻的具体网址
                detail_url = 'https://dcnewsj.joins.com' + i.xpath(
                    './strong[@class="headline mg"]/a/@href').extract_first()
                title = i.xpath('./strong[@class="headline mg"]/a/text()').extract_first()
                # 获取新闻的摘要
                abstract = i.xpath('./span[@class="lead"]/a/text()').extract_first()
                if not abstract:
                    abstract = "abstract is none"  # 如果摘要为空，则设为空字符串
                # 获取每个新闻的图片
                images = []
                image = i.xpath('./span[@class="thumb"]/a/img/@src').extract_first()
                if image is not None:
                    images.append(image)
                # 将获取的信息通过response的meta传递到下一个函数
                response.meta['pub_time'] = pub_time
                response.meta['title'] = title
                response.meta['abstract'] = abstract
                response.meta['images'] = images
                yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)
        else:
            return

        # 翻页逻辑
        next_page_url = f'https://dcnewsj.joins.com/all?page={self.page}'
        yield scrapy.Request(next_page_url, callback=self.parse, meta=response.meta)
        self.page += 1  # 增加页数

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        category1 = 'News'
        title = response.meta['title']
        abstract = response.meta['abstract']
        body = response.xpath('//html/body/div[1]/div/div[4]/div[2]/div[2]/text()').extract()
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
        item['images'] = response.meta['images']
        item['pub_time'] = response.meta['pub_time']
        if body != '':
            yield item
            # print(item['pub_time'])
            # print(f"第【{self.i}】个网站抓取成功->{response.request.url}")
            self.i = self.i + 1
        # print(item['images'])
