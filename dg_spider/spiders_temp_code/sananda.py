


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
import re

# encoding: utf-8

# 英语月份对照表
ENGLISH_MONTH = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12',
}

# author : 李玲宝
# 网站新闻量小（90+），可以从一个链接调出新闻数据，因此没写时间截止函数
# check: 凌敏  pass
class SanandaSpider(BaseSpider):
    name = 'sananda'
    website_id = 1895
    language_id = 1779
    proxy = '02'
    start_urls = ['https://api.sananda.in/api/jsonws/contentservice.content/Section-other-stories/category-id/46866/start/0/end/2000']
    # 原start_urls: https://www.sananda.in/galpo?sectionid=46866&secName=Golpo

    def parse(self, response):
        article = response.json()
        for i in article:
            url = 'https://api.sananda.in/api/jsonws/contentservice.content/get-story/article-id/' + i['link']
            yield scrapy.Request(url, callback=self.parse_item, meta={'category1': i['categoryName']})

    def parse_item(self, response):
        article = response.json()
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = article['title']
        t = article['publishDate'].split(' ')
        item['pub_time'] = f'{t[-1]}-{OldDateUtil.EN_1866_DATE[t[1]]}-{t[2]}' + ' 00:00:00'
        item['images'] = ['https://api.sananda.in/image/journal/article?img_id=' + article['imageId']] if article['image'] else []
        soup = BeautifulSoup(article['body'], 'html.parser')
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('p') if i.text.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
