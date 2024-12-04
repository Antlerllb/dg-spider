

  # 确保导入正确的Item类
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
'''
    Author：纪小翠
    Date：2024.9.24
    Country：阿拉伯语国家
    Language：阿拉伯语
    URL：https://www.sabanew.net/
'''


class SabanewSpider(BaseSpider):  # 类名重命名
    author = '纪小翠'
    name = 'sabanew'  # name的重命名
    website_id = 2647  # id一定要填对！
    language_id = 1748  # id一定要填对！
    # lan_num = 1
    start_urls = ['https://www.sabanew.net']
    base_url = "https://www.sabanew.net/category/ar"

    def parse(self, response):
        # 进入菜单分类
        for i in range(0, 6):
            category = response.urljoin(f'/category/ar/{i}/')
            meta_date = {"i": i}
            yield scrapy.Request(url=category, callback=self.parse_page, meta=meta_date)

    # 菜单第一页
    def parse_page(self, response):
        # 翻页
        start_page = 1
        end_page_text = response.xpath(
            '//div[@class="col-md-9"]/div[@class="col-md-12 navbtoonslinks "]/a[last()]/text()').get()
        end_page = int(end_page_text)

        for page in range(end_page, start_page - 1, -1):
            page_url = response.urljoin(f'/category/ar/{response.meta["i"]}/{page}')
            meta_date={"i": response.meta["i"]}
            yield scrapy.Request(url=page_url, callback=self.parse_url, meta=meta_date)

    def parse_url(self, response):
        # 获取菜单
        category_id = response.meta["i"]
        if category_id == 0:
            category1 = "当地"
        if category_id == 1:
            category1 = "阿拉伯和国际"
        if category_id == 2:
            category1 = "报告与对话"
        if category_id == 3:
            category1 = "经济"
        if category_id == 4:
            category1 = "运动"
        if category_id == 5:
            category1 = "文化"

        block = response.xpath('//div[@class="col-md-9"]/div[@class="col-md-12"]')

        for i in block:
            # 新闻具体链接
            news_url = response.urljoin(i.xpath('./div[@class="col-md-12"]/a/@href').extract_first())
            # 标题
            title = i.xpath('./div[@class="col-md-12"]/a/text()').extract_first()
            # 图片
            images = []
            image = i.xpath('./div[@class="col-md-12"]/img/@src').extract_first()
            if image is not None:
                images.append(image)
            # 摘要
            abstract = i.xpath('./div[@class="col-md-12"]/div[@class="mainText"]/text()').extract_first()

            # 将必要信息存入meta数据
            meta_data = {
                'category1': category1,
                'title': title,
                'abstract': abstract,
                'images': images
            }
            yield scrapy.Request(url=news_url, callback=self.parse_item, meta=meta_data)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)

        # 时间
        date_text = response.xpath('//div[@class="col-md-9"]/div[2]/text()').get()

        # 格式化
        if date_text:
            date_text = date_text.strip().strip('[]')
            # 确保日期格式与提取的文本匹配
            date = datetime.strptime(date_text, '%d/%m/%Y %H:%M')
            pub_time = date.strftime('%Y-%m-%d %H:%M')
        else:
            pub_time = None

        text_blocks = response.xpath(
            '//div[@class="col-md-12" and @style="direction: ltr; text-align: left;"]/font[@_mstmutation="1"]/text()'
        ).extract()
        body = ''
        for block in text_blocks:
            lines = block.split('\n')
            for line in lines:
                if line.strip():
                    body += '    ' + line.strip() + '\n'

        # 确保在文本块的最后添加一个换行符
        body += '\n'

        # 设置item数据
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['images'] = response.meta['images']
        item['body'] = body
        item['pub_time'] = pub_time

        yield item
