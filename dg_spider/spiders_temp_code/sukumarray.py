


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
# 文章内容为诗歌，没有时间，都给了'1970-01-01 00:00:00'（因此也没写时间截止函数）;文章都没有图片，没有二级标题
# check：凌敏 pass
class SukumarraySpider(BaseSpider):
    name = 'sukumarray'
    website_id = 1905
    language_id = 1779
    proxy = '02'
    is_http = 1
    start_urls = ['http://sukumarray.freehostia.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('#menu_buttons a')[:-1]
        for i in category1:
            yield scrapy.Request('http://sukumarray.freehostia.com/' + i['href'], callback=self.parse_page)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#five a'):
            url = 'http://sukumarray.freehostia.com/' + i['href']
            yield Request(url, callback=self.parse_item, meta={'category1': soup.select_one('#cat_header_div').text.strip()})

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('#header_div').text.strip()
        item['pub_time'] = '1970-01-01 00:00:00'
        item['images'] = []
        if soup.select_one('table') is not None:
            item['body'] = '\n'.join(i.text.strip() for i in soup.select('table td') if i.text.strip() != '')
        else:
            item['body'] = '\n'.join(i.strip() for i in soup.select_one('#article_content').text.split('\n') if i.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
