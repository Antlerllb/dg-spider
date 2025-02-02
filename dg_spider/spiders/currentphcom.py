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



# author: 武洪艳
class CurrentphcomSpider(BaseSpider):
    name = 'currentphcom'
    website_id = 1177
    language_id = 1866
    # allowed_domains = ['currentph.com/']
    start_urls = ['https://currentph.com/']  # https://currentph.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#menu-cns-menu-1 > li > a')[1:]
        for category in categories:
            category_url = category.get('href')
            yield Request(url=category_url, callback=self.parse_page, meta={'category1': category.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        if OldDateUtil.time is not None:
            t = soup.select('div.td-pb-span8.td-main-content .item-details span.td-post-date')[-1].text.replace(',',' ').split(' ')
            last_time = "{}-{}-{}".format(t[3], str(OldDateUtil.EN_1866_DATE[t[0]]).zfill(2), t[1]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            articles = soup.select('div.td-pb-span8.td-main-content .item-details > h3 a')
            for article in articles:
                article_url = article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select('div.td-pb-span8.td-main-content .page-nav.td-pb-padding-side > a'):
                next_page = soup.select('div.td-pb-span8.td-main-content .page-nav.td-pb-padding-side > a')[-1].get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            else:
                self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('header.td-post-title > h1').text.strip()
        tt = soup.select_one('header.td-post-title > div > span').text.replace(',',' ').split(' ')
        item['pub_time'] = "{}-{}-{}".format(tt[3], str(OldDateUtil.EN_1866_DATE[tt[0]]).zfill(2), tt[1]) + ' 00:00:00'
        item['images'] = [img.get('src') for img in soup.select('div.td-post-content.tagdiv-type img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('div.td-post-content.tagdiv-type') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = soup.select_one('div.td-post-content.tagdiv-type').text
        return item
