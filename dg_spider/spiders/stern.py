from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

#check:wpf pass
class SternSpider(BaseSpider):  # author：田宇甲
    name = 'stern'
    website_id = 1770
    language_id = 1898
    start_urls = ['https://www.stern.de/news/']  # 这个网站只有最近24小时的新闻，非常新鲜但是以前的新闻找不到了

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .group__items article'):
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(i.time).split('datetime="')[1].split('+')[0].replace('T', ' ')) >= int(OldDateUtil.time):
                meta = {'pub_time_': str(i.time).split('datetime="')[1].split('+')[0].replace('T', ' '), 'title_': i.select_one(' .teaser__headline.u-typo.u-typo--teaser-title-small').text.strip(), 'category1_': 'News'}
                yield Request(i.a['href'], callback=self.check_check, meta=meta)

    def check_check(self, response):
        item, soup = NewsItem(), BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        try:
            item['body'] = '\n'.join([i.text for i in soup.select(' .article__body.js-article-body p')])
            item['abstract'] = soup.select_one(' .article__body.js-article-body p').text.strip()
        except:
            item['body'] = soup.select_one(' .article__body.js-article-body').text
            item['abstract'] = soup.select_one(' .article__top').text
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = [soup.select_one(' .article__header img')['src']]
        yield item
