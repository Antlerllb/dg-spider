


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
# 网站是以前孟加拉语写好但是忘记提交的，不是乌尔都语的，id都是对的
# 网站的时间是纯孟加拉语的，python没法翻译，就都给了1970-01-01 00:00:00
# check：凌敏 pass
class SachalayatanSpider(BaseSpider):
    name = 'sachalayatan'
    website_id = 1908
    language_id = 1779
    is_http = 1
    start_urls = ['http://en.sachalayatan.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#subnavlist>li>a'):
            url = i['href'] + '?page='
            yield scrapy.Request(url + '0', callback=self.parse_page, meta={'category1': i.text.strip(), 'page': 0, 'url': url})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#node-preview'):
            yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        if soup.select_one('.pager-next') is not None:
            response.meta['page'] += 1
            yield Request(response.meta['url'] + str(response.meta['page']), callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1').text.strip()
        item['pub_time'] = '1970-01-01 00:00:00'
        item['images'] = [img.get('src') for img in soup.select('.node img')]
        item['body'] = '\n'.join(i.strip() for i in soup.select_one('#node-full .content').text.split('\n') if i.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
