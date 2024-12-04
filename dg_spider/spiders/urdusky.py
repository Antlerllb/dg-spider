


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
# check: 凌敏 pass
# 我爬的是那个“乌尔都语”文档的网站，对接的同学说审核爬虫的人填id,那个id是我乱填的（不填会报错）
class UrduskySpider(BaseSpider):
    name = 'urdusky'
    website_id = 2095
    language_id = 2238
    start_urls = ['http://www.urdusky.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('#menu-1-a52282c a')
        for i in category1[1:]:
            yield scrapy.Request(i['href'], callback=self.parse_page, meta={'category1': i.text.strip()})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('article')
        if OldDateUtil.time is not None:
            last_time = block[-1].select_one('time')['datetime'][:10] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                response.meta['pub_time'] = i.select_one('time')['datetime'][:10] + ' 00:00:00'
                yield Request(i.select_one('.title a')['href'], callback=self.parse_item, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = []
        for i in soup.select('.single-container img'):
            if i.get('src'):
                item['images'].append(i.get('src'))
            else:
                item['images'].append(i.get('data-src'))
        item['body'] = '\n'.join(i.strip() for i in soup.select_one('.entry-content').text.split('\n') if i.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        if item['images']:
            return item
