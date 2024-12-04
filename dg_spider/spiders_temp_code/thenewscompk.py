
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



class ThenewscompkSpider(BaseSpider):
    name = "thenewscompk"
    start_urls = ["https://www.thenews.com.pk/"]
    author = '吴雨奔'
    website_id = 2284  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1

    '''

    需要修改默认请求头的accept-encoding才可以爬
    BASE_DEFAULT_REQUEST_HEADERS = {
        'Accept-Encoding': 'gzip, deflate',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/90.0.4430.72 Safari/537.36"
    }
    '''

    def parse(self, response):
        url_list = response.xpath('//div[@class="menu"]/ul/li/a/@href').extract()
        for url in url_list:
            if any(category in url for category in ['stories', 'national', 'sports', 'world']):

                yield scrapy.Request(url, callback=self.parse_articles1)
            elif any(category in url for category in ['business', 'entertainment', 'sci-tech', 'health']):

                yield scrapy.Request(url, callback=self.parse_articles2)

    def parse_articles1(self, response):
        news_urls_list = response.xpath('//*[@class="detail-center"]/div/ul/li/div/a/@href').extract()
        pic_list = response.xpath('//*[@class="detail-center"]/div/ul/li/div/a/img/@src').extract()
        for news_url, pic_url in zip(news_urls_list, pic_list):
            yield scrapy.Request(
                url=news_url,
                meta={'pic_url': pic_url},
                callback=self.parse_detail
            )

    def parse_articles2(self, response):
        news_urls_list = response.xpath('//div[@class="new_category"]/div/div/div/div[1]/a/@href').extract()
        pic_list = response.xpath('//div[@class="new_category"]/div/div/div/div[1]/a/img/@src').extract()
        for news_url, pic_url in zip(news_urls_list, pic_list):
            yield scrapy.Request(
                url=news_url,
                meta={'pic_url': pic_url},
                callback=self.parse_detail
            )

    def parse_detail(self, response):

        date_str = response.xpath('//div[@class="category-date"]/text()').extract_first().strip()
        # 将日期字符串解析为 datetime 对象
        dt = datetime.strptime(date_str, '%B %d, %Y')
        # 将 datetime 对象格式化为新的字符串格式
        pt = dt.strftime('%Y-%m-%d 00:00:00')
        if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(pt):
            pic_url = str(response.meta['pic_url'])
            item = NewsItem(language_id=self.language_id)
            title = response.xpath('//div[@class="detail-heading"]/h1/text()').extract_first()
            abstract = response.xpath(
                '//div[@class="detail-heading"]/div[2]/h2/text()').extract_first().strip()
            article = response.xpath('//div[@class="story-detail"]/p/text()').extract()
            content = ''
            if len(article) > 1:
                content = "\n".join(article)
            else:
                content = "\n".join(abstract) + "\n".join(article)
            item['abstract'] = abstract
            item['body'] = content
            item['images'] = [pic_url]
            item['category1'] = response.xpath('//div[@class="category-name"]/span/a/text()').extract_first()
            item['pub_time'] = pt
            item['title'] = title
            item['language_id'] = 1866
            yield item


