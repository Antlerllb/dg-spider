


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
# 因为文章内容是经典诗歌，所以没有时间，我都给了“1970-01-01 00:00:00”；文章内容都没有图片
# check: 凌敏 pass
class BanglaSpider(BaseSpider):
    name = 'bangla'
    website_id = 1904
    language_id = 1779
    start_urls = ['https://www.bangla-kobita.com/famouspoets/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.select('.famous-poets>div')
        for i in menu:
            url = 'https://www.bangla-kobita.com' + i.select_one('a')['href'] + '?t=p&pp='
            yield scrapy.Request(url + '1', callback=self.parse_page, meta={'category1': i.select_one('a')['title'], 'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#poem>.post-list tr')[1:]:
            yield Request('https://www.bangla-kobita.com' + i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        if (soup.select_one('.PagedList-skipToNext') is not None):
            response.meta['page'] += 1
            yield Request(response.meta['url'] + str(response.meta['page']), callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1>span').text.strip()
        item['pub_time'] = OldDateUtil.get_now_datetime_str()
        item['images'] = [img.get('src') for img in soup.select('.post-content img')]
        item['abstract'] = soup.select_one('.post-content>p').text.strip().split('\n')[0]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('.post-content>p'))
        return item
