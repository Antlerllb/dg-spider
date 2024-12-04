from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author : 胡楷
# chekc: pys
class eksisozlukSpider(BaseSpider):
    name = 'eksisozluk'
    website_id = 1812
    language_id = 2227
    allowed_domains = ['eksisozluk.com']
    start_urls = ['https://eksisozluk.com']
    proxy = "02"

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#sub-navigation a')[0:17]
        del categories[6]
        del categories[2]
        for category in categories:
            category_url = 'https://eksisozluk.com' + category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('ul.topic-list.partial > li > a')
        flag = True
        if OldDateUtil.time is not None:
            last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = 'https://eksisozluk.com' + article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = 'https://japantoday.com' + soup.select_one('div.quick-index-continue-link-container > a').get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('#topic > #title > a > span').text.strip()
        item['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['images'] = None
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.content') if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item
