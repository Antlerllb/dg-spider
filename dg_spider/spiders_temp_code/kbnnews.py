from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy





class KbnnewsSpider(BaseSpider):
    name = 'kbnnews'
    website_id = 2691
    language_id = 2275
    author = '马波生'
    start_urls = ['https://kbn.news/']

    @staticmethod
    def change_time(date_str):
        # 转换为日期对象
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        # 格式化为所需的字符串格式
        formatted_date = date_obj.strftime("%Y-%m-%d")
        formatted_time = formatted_date + ' 00:00:00'
        return formatted_time

    def parse(self, response):
        category1 = response.xpath('//*[@id="menu-primary-1"]/li/a/text()').extract()
        links = ['https://kbn.news/archives/category/%e1%9e%82%e1%9f%92%e1%9e%9a%e1%9f%84%e1%9f%87%e1%9e%90%e1%9f%92%e1%'
                 '9e%93%e1%9e%b6%e1%9e%80%e1%9f%8b%e1%9e%85%e1%9e%9a%e1%9e%b6%e1%9e%85%e1%9e%9a', 'https://kbn.news/archives/category/world-news']
        for link in links:
            for i in range(1, 50):
                real_link = link + f'/page/{i}'
                yield scrapy.Request(url=real_link, callback=self.parse_page,
                                        meta={'category1': category1})

    def parse_page(self, response):
        news_links = response.xpath('//*[@id="td-outer-wrap"]/div/div[2]/div/div[2]/div[1]/div/div[2]/div[1]/div/div[2]'
                                    '/h3/a/@href').extract()
        if news_links is None:
            return
        pub_times = response.xpath('//*[@id="td-outer-wrap"]/div/div[2]/div/div[2]/div[1]/div/div/div/div/div[2]/div'
                                   '/span/time/text()').extract()
        pub_time = []
        judge_pub_time = []
        for t in pub_times:
            cleaned_time = self.change_time(t)
            pub_time.append(cleaned_time)
            judge_pub_time.append(cleaned_time)
        for l in news_links:
            index = news_links.index(l)
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(judge_pub_time[index]) < OldDateUtil.time:
                return
            else:
                yield scrapy.Request(url=l, callback=self.parse_detail, meta={"category1": response.meta["category1"],
                                                                                "pub_time": pub_time[index]})

    def parse_detail(self, response):
        item = NewsItem(language_id=self.language_id)
        category1 = response.meta["category1"]
        pub_time = response.meta["pub_time"]
        title = response.xpath('//*[@id="td-outer-wrap"]/div/div[2]/div/article/div[1]/div/div/header/h1/text()').extract()
        body = ''
        bodys = response.xpath('//*[@id="td-outer-wrap"]/div/div[2]/div/article/div[2]/div/div/div/p/text()').extract()
        for b in bodys:
            body += b.strip() + '\n'
        abstracts = response.xpath('//*[@id="td-outer-wrap"]/div/div[2]/div/article/div[2]/div/div/div/p[1]/text()').extract()
        abstract = [a.strip() for a in abstracts][0]
        image = response.xpath('//*[@id="td-outer-wrap"]/div/div[2]/div/article/div[2]/div/div/div/p/img/@src').extract_first()
        if image is not None:
            image = [image]
        else:
            image = []
        category = ''
        for c in category1:
            category += c
        item['title'] = title[0]
        item['abstract'] = abstract
        item['body'] = body
        item['category1'] = category
        item['images'] = image
        item['pub_time'] = pub_time
        yield item


