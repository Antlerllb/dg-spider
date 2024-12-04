
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




class GeotvSpider(BaseSpider):
    name = "geotv"
    allowed_domains = ["geo.tv"]
    start_urls = ["https://www.geo.tv/"]
    author = '吴雨奔'
    website_id = 2304  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    proxy = '02'

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
        items = response.xpath('//div[@class="container"]/nav/ul/li')
        for item in items:
            url = item.xpath('./a/@href').extract_first()
            if url and any(category in url for category in ['latest-news', 'pakistan', 'world', 'sports','showbiz']):
                category= item.xpath('./a/text()').extract_first()
                yield scrapy.Request(url,meta={'category':category}, callback=self.parse_articles1)

    def parse_articles1(self, response):
        category = response.meta['category']
        news_urls_list = response.xpath('//div[@class="list"]/ul/li/a/@href').extract()
        # pic_list = response.xpath('//*[@class="detail-center"]/div/ul/li/div/a/img/@src').extract()
        for news_url in news_urls_list:
            yield scrapy.Request(
                url=news_url,
                meta={'category': category},
                callback=self.parse_detail
            )

    def parse_detail(self, response):
        category = response.meta['category']
        date_str = response.xpath('//p[@class="post-date-time"]/text()').extract_first().strip()
        # 将日期字符串解析为 datetime 对象
        dt = datetime.strptime(date_str, '%B %d, %Y')
        # 将 datetime 对象格式化为新的字符串格式
        pt = dt.strftime('%Y-%m-%d 00:00:00')
        if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(pt):

            item = NewsItem(language_id=self.language_id)
            pic_url = response.xpath('//div[@class="content-area"]/div/figure/img/@src').extract_first()
            # print(f"pic_url value: {pic_url}")
            title = response.xpath('//div[@class="story-area"]/h1/text()').extract_first()
            abstract = response.xpath('//div[@class="story-area"]/h1/text()').extract_first()
            article = response.xpath('//div[@class="content-area"]/p').extract()
            if len(article) > 1:
                content = "\n".join(article)
            else:
                content = "\n".join(abstract) + "\n".join(article)
            item['abstract'] = abstract
            item['body'] = content
            if pic_url is not None and pic_url != '':
                item['images'] = [pic_url]
            else:
                item['images'] = []
            item['category1'] = category
            item['pub_time'] = pt
            item['title'] = title
            item['language_id'] = 1866
            yield item


