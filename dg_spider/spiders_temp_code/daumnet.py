from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy





class DaumnetSpider(BaseSpider):
    name = 'daumnet'
    proxy = '02'
    website_id = 2024
    language_id = 1991
    author = '马波生'
    start_urls = ['https://news.daum.net/']

    def change_time(self, time):
        # 原始时间字符串
        date_str = time
        # 将字符串转换为 datetime 对象
        date_obj = datetime.strptime(date_str, '%Y. %m. %d. %H:%M')
        # 格式化为所需的格式
        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
        formatted_date = formatted_date + ':00'
        return formatted_date

    def parse(self, response):
        category1 = response.xpath('//*[@id="gnbContent"]/div/ul/li/a/span/text()').extract()
        page_link = response.xpath('//*[@id="gnbContent"]/div/ul/li/a/@href').extract()
        for link in page_link[1:8]:
            for i in range(1, 69):
                links = 'https://news.daum.net/breakingnews' + link
                links = links.rstrip('/')
                links = links + f'?page={i}'
                yield scrapy.Request(url=links, callback=self.parse_page,
                                     meta={'category1': category1})

    def parse_page(self, response):
        category1 = response.meta['category1']
        news_links = response.xpath('//*[@id="mArticle"]/div[3]/ul/li/div/strong/a/@href').extract()
        for link in news_links:
            yield scrapy.Request(url=link, callback=self.parse_detail,
                                 meta={'category1': category1})

    def parse_detail(self, response):
        item = NewsItem(language_id=self.language_id)
        pub_time = response.xpath('//*[@id="mArticle"]/div[1]/div[1]/span/span/text()').extract()
        pub_time = self.change_time(pub_time[0])
        if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
            return
        category1 = ''
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').extract()  # 标题
        abstract = response.xpath('//*[@id="mArticle"]/div[2]/strong/text()').extract()  # 摘要
        if len(abstract) == 0:
            abstract = response.xpath('//*[@id="mArticle"]/div[2]/div/section/p[1]/text()').extract()
        body = ''
        bodys = response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').extract()  # 主体
        for b in bodys:
            body += b.strip() + '\n\n'
        image = [response.xpath('//*[@id="mArticle"]/div[2]/div/section/figure/p/img/@src').extract_first()]
        categories = response.meta['category1']
        for category in categories:
            category1 += category + ' '
        item['title'] = title[0]
        item['abstract'] = abstract[0]
        item['body'] = body
        item['category1'] = category1
        item['images'] = []
        item['pub_time'] = pub_time
        if body != '':
            yield item





