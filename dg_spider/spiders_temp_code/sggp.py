


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

# author : 李玲宝

# check:why

class SggpSpider(BaseSpider):
    name = 'sggp'
    website_id = 253
    language_id = 2242
    start_urls = ['http://www.sggp.org.vn/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.select('nav.navigation li')[1:]
        for i in menu:
            url = 'http://www.sggp.org.vn' + i.select_one('a')['href'] + 'trang-1.html'
            yield scrapy.Request(url, callback=self.parse_page, meta={'category1': i.select_one('a')['title'], 'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('#box-content div.zone-content article')
        flag = True
        if OldDateUtil.time is not None:
            last_time = block[-1].select_one('time')['datetime'] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                yield Request('http://www.sggp.org.vn' + i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            response.meta['page'] += 1
            url = response.meta['url'].split('trang-')[0] + 'trang-' + str(response.meta['page']) + '.html'  # 页码+1后的url
            yield Request(url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1.cms-title').text
        item['abstract'] = soup.select_one('header.article-hdr div.summary').text.strip()
        item['pub_time'] = soup.select_one('div.meta-info time')['datetime'] + ' 00:00:00'
        item['images'] = [img.get('src') for img in soup.select('div.cms-body img')]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('div.cms-body>p') if (i.text.strip() != ''))
        return item
