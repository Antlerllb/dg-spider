


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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

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
    'December': '12'
}

# author : 李玲宝
# check: 凌敏 pass
# 新闻量小
class AbasarSpider(BaseSpider):
    name = 'abasar'
    website_id = 1893
    language_id = 1779
    start_urls = ['https://abasar.net']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-main-menu li')[1:-1]:
            yield scrapy.Request(i.select_one('a')['href'], callback=self.parse_page, meta={'category1': i.select_one('a').text.strip()})

    def parse_page(self, response):  # 新闻量小，不用翻页
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.blog-layouts>div'):
            tt = i.select('.blog-bottom-content-holder>ul>li')[1].text.strip().split(' ')
            response.meta['pub_time'] = time.strftime('%Y-%m-%d', time.strptime(f"{tt[2]}.{OldDateUtil.EN_1866_DATE[tt[0]]}.{tt[1][:-1]}", '%Y.%m.%d')) + ' 00:00:00'
            yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta, dont_filter=True)
        self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['abstract'] = soup.select_one('.elementor-clearfix').text.strip().split('\n')[0]
        if (soup.select_one('.elementor-heading-title') is not None):  # 有的文章没有标题
            item['title'] = soup.select_one('.elementor-heading-title').text.strip()
        else:
            item['title'] = item['abstract']
        item['body'] = '\n'.join(i.strip() for i in soup.select_one('.elementor-clearfix').text.strip().split('\n') if (i.strip() != ''))
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.elementor-clearfix img')]
        return item
