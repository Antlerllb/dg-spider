


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
# check: 凌敏 pass
class VnexpressSpider(BaseSpider):
    name = 'vnexpress'
    website_id = 254
    language_id = 2242
    start_urls = ['http://vnexpress.net/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.select("nav.main-nav > ul > li")
        for i in menu[1:4] + menu[6:-3]:
            url = 'http://vnexpress.net' + i.select_one('ul a')['href']
            yield scrapy.Request(url, callback=self.parse2, meta={'category1': i.select_one('ul a')['title']})

    def parse2(self, response):
        meta = response.meta
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.select("ul.ul-nav-folder > li")
        for i in menu:
            if not (i.select_one('a')['href'].startswith('http')):
                url = 'http://vnexpress.net' + i.select_one('a')['href']
                meta['category2'] = i.select_one('a')['title']
                meta['url'] = url
                meta['page'] = 1
                yield scrapy.Request(url, callback=self.parse_page, meta=meta)

    # 新闻列表页面没有时间，要点进去才能看到时间
    def parse_last_time(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        tt = soup.select_one('span.date').text.split(', ')[1]
        yield time.strftime('%Y-%m-%d', time.strptime(tt, '%d/%m/%Y'))

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if (soup.select_one('.has-border-right article') is None):  # 没有文章了，爬虫结束，退出函数
            self.logger.info("时间截止")
            return 1
        block = soup.select('.has-border-right article')[1:-1]
        flag = True
        if OldDateUtil.time is not None:
            # 新闻列表页面没有时间，要点进去才能看到时间
            last_time = self.parse_last_time(block[-1].select_one('a')['href'])
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            response.meta['page'] += 1
            url = response.meta['url'].split('-p')[0] + '-p' + str(response.meta['page'])  # 页码+1后的url
            yield Request(url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('h1.title-detail').text
        item['abstract'] = soup.select_one('p.description').text
        tt = soup.select_one('span.date').text.split(', ')[1]
        item['pub_time'] = time.strftime('%Y-%m-%d', time.strptime(tt, '%d/%m/%Y'))
        item['images'] = [img.get('src') for img in soup.select('article.fck_detail img')]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('article.fck_detail p'))
        return item
