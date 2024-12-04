

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




class BrecorderSpider(BaseSpider):
    author = '苏钰婷'
    name = 'brecorder'  # name的重命名
    website_id = 2305
    language_id = 2238
    lan_num = 1
    start_urls = ['https://www.brecorder.com/br-research/analysis-and-comments/',
                  'https://www.brecorder.com/br-research/brief-recordings/',
                  'https://www.brecorder.com/business-finance/real-estate/',
                  'https://www.brecorder.com/business-finance/money-banking/',
                  'https://www.brecorder.com/business-finance/companies/',
                  'https://www.brecorder.com/business-finance/industry/',
                  'https://www.brecorder.com/business-finance/taxes/',
                  'https://www.brecorder.com/business-finance/interest-rates/',
                  'https://www.brecorder.com/editorials/',
                  'https://www.brecorder.com/opinion/',
                  'https://www.brecorder.com/technology/',
                  'https://www.brecorder.com/life-style/',
                  'https://www.brecorder.com/sports/',
                  'https://www.brecorder.com/perspectives/',
                  'https://www.brecorder.com/pakistan/',
                  'https://www.brecorder.com/supplements/',
                  'https://www.brecorder.com/print/'
                  ]

    def start_requests(self):
        today = datetime.now().strftime('%Y-%m-%d')
        for url in self.start_urls:
            yield scrapy.Request(url + today, callback=self.parse)

    def parse(self, response):
        articles = response.xpath('//div[@class="flex flex-col w-full"]')
        for article in articles:
            item = {}
            article_url = article.xpath('.//article/div/div/h2/a/@href').get()
            yield scrapy.Request(response.urljoin(article_url), callback=self.parse_article, meta={'item': item})

            # 提取发布时间
            url_date = response.url.split('/')[-1]  # 提取URL中的日期部分
            pub_time = datetime.strptime(url_date, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
            # 时间截至
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            item['pub_time'] = pub_time

        # 查找是否存在分页链接
        next_page = response.xpath('//a[contains(text(), "Previous Day")]/@href').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article(self, response):
        item = response.meta['item']
        # 提取标题
        title = OldFormatUtil.remove_invalid_utf8(response.xpath('//h1[@class="story__title      text-7.5  font-normal    mb-4  "]//text()').get())
        # 如果标题为空，则将其值设为"None"
        item['title'] = title if title else "None"

        # 提取分类
        category_str = ' '.join(response.xpath('//span[@class="badge  inline-flex    btn mr-2 bg-gray-600 text-gray-300        mb-2  align-middle"]//a/span/text()').getall())
        # 若为空，则将其设置为"None"
        item['category1'] = category_str if category_str else "None"

        # 提取图片
        image_url = response.xpath('//div[contains(@class,"media__item")]/picture/img/@src').extract_first()
        if image_url:
            item['images'] = [image_url]
        else:
            item['images'] = []

        # 提取正文，并去除空行
        body_paragraphs = response.xpath('//div[@class="story__content  overflow-hidden          pt-2  mt-2"]//p/text()').getall()
        body_paragraphs = [para.strip() for para in body_paragraphs if para.strip() != '']
        body_text = '\n'.join(body_paragraphs)  # 将列表转换为字符串
        body_text = OldFormatUtil.remove_invalid_utf8(body_text)  # 移除无效的utf-8字符
        item['body'] = body_text

        # 提取摘要
        first_sentence = body_paragraphs[0].split('.')[0] if '.' in body_paragraphs[0] else body_paragraphs[0].split()[0]
        item['abstract'] = first_sentence

        # 如果正文只有一段，将正文和摘要拼接起来
        if len(body_paragraphs) == 1:
            item['body'] = item['body'] + '\n' + item['abstract']

        # 网站语言为英语
        item['language_id'] = 1866

        yield item