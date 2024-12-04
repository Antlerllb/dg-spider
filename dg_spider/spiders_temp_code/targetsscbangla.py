


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
# check；凌敏 id错误，已改 pass
# 文章没有时间，都给了1970-01-01 00:00:00
class TargetsscbanglaSpider(BaseSpider):
    name = 'targetsscbangla'
    website_id = 1890
    language_id = 1779
    proxy = '02'
    start_urls = ['https://www.targetsscbangla.com/modern-bengali-literature']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select_one('#menu-item-30').select('li.menu-item-depth-1')[:3]:
            for j in i.select('li.menu-item-depth-2'):
                if not (j.select_one('a')['href'].endswith('97-2')):
                    yield scrapy.Request(j.select_one('a')['href'], callback=self.parse_page, meta={'category1': i.select_one('a').text.strip(), 'category2': j.select_one('a').text.strip()})

    # 新闻量少，不用设置翻页（因为只有一页）
    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('.main-col .bp-entry')
        for i in block:
            yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('h1.post-tile').text.strip()
        if (soup.select_one('.entry-content>p') is not None):
            item['abstract'] = soup.select_one('.entry-content>p').text.strip()
            item['body'] = '\n'.join(i.text.strip() for i in soup.select('.entry-content>p'))
        else:
            item['abstract'] = soup.select_one('.entry-content>div').text.strip()
            item['body'] = '\n'.join(i.text.strip() for i in soup.select('.entry-content>div'))
        item['pub_time'] = OldDateUtil.get_now_datetime_str()
        item['images'] = [img.get('src') for img in soup.select('.base-box .feature-img img')[1:]]
        return item
