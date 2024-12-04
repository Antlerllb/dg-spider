from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author:胡楷
# check: pys
class polyglotclubSpider(BaseSpider):
    name = 'polyglotclub'
    website_id = 1847
    language_id = 2227
    allowed_domains = ['polyglotclub.com']
    start_urls = ['https://polyglotclub.com/help/translate-turkish']  # https://polyglotclub.com/help/language-learning-tips/chinese-characters/translate-turkish


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('div.col-md-12 > ul > li > a')
        for category in categories:
            category_url = 'https://polyglotclub.com/' + category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)


    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('ul.notification > li > a')
        for article in articles:
            article_url = 'https://polyglotclub.com/' + article.get('href')
            yield Request(url=article_url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('div.col-md-12 > div > h1').text.strip()
        item['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 该网站无pub_time 用爬取时间替代
        item['images'] = [img.get('src') for img in soup.select('div.Smargin-bottom.pg_help_box > img')]
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.Smargin-bottom.pg_help_box') if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item


