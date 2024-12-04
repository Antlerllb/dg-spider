


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
# chenck: 凌敏 pass
# 因为文章内容是经典诗歌，所以没有时间，我都给了“1970-01-01 00:00:00”；文章内容都没有图片
class NazrulgeetiSpider(BaseSpider):
    name = 'nazrulgeeti'
    website_id = 1903
    language_id = 1779
    start_urls = ['https://www.nazrulgeeti.org/all-song-list?start=1500']

    def parse(self, response):  # 文章有个页面可以调出本网站所有诗歌，所以可以直接从parse回调parse_item
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.select('table.category tr')
        for i in article:
            yield scrapy.Request('https://www.nazrulgeeti.org' + i.select_one('a')['href'], callback=self.parse_item, meta={'category1': soup.select_one('.content-category>h2').text.strip()})


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1>span').text.strip()
        item['pub_time'] = OldDateUtil.get_now_datetime_str()
        item['images'] = []
        item['body'] = ''  # 有一些行有奇怪的空格，所以要这样写
        for i in soup.select_one('.tab-content pre').text.strip().split('\n'):
            item['body'] = item['body'] + i.strip() + '\n'
        item['body'] = item['body'].strip()
        item['abstract'] = item['body'].split('\n')[0]
        return item
