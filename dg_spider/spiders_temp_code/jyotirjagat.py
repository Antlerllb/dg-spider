


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# author : 李玲宝
# 新闻量少，时间很老（三四年前），就没写时间截止函数
# check：凌敏 pass
class JyotirjagatSpider(BaseSpider):
    name = 'jyotirjagat'
    website_id = 1907
    language_id = 1779
    proxy = '02'
    start_urls = ['https://jyotirjagat.wordpress.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('.entry-content>p>a')[4:]
        for i in category1:
            yield scrapy.Request(i['href'], callback=self.parse_page, meta={'category1': i.select_one('img')['alt']})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#main>article'):
            url = i.select_one('a')['href']
            response.meta['pub_time'] = i.select_one('.entry-date').text.strip().replace('/', '-') + ' 00:00:00'
            yield Request(url, callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1.entry-title').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.entry-content img')]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('.entry-content p') if i.text.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
