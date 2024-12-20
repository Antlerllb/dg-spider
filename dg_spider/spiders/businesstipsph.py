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



# author : 武洪艳
class BusinesstipsphSpider(BaseSpider):
    name = 'businesstipsph'
    website_id = 1187
    language_id = 1866
    # allowed_domains = ['businesstips.ph/']
    start_urls = ['https://businesstips.ph/']  # https://businesstips.ph/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#menu-main-menu > li > a')[2:5]
        for category in categories:
            yield Request(url=category.get('href'), callback=self.parse_page,  meta={'category1': category.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.content-sidebar-wrap > main.content > article > header')
        if OldDateUtil.time is not None:
            t = articles[-1].select_one('.entry-meta .entry-time').text.replace(',', ' ').split(' ')
            last_time = "{}-{}-{}".format(t[3], str(OldDateUtil.EN_1866_DATE[t[0]]).zfill(2), t[1]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.select_one('.entry-meta .entry-time').text.replace(',', ' ').split(' ')
                pub_time = "{}-{}-{}".format(tt[3], str(OldDateUtil.EN_1866_DATE[tt[0]]).zfill(2), tt[1]) + ' 00:00:00'
                article_url = article.select_one('.entry-title a').get('href')
                title = article.select_one('.entry-title a').text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('main.content > div > ul > li.pagination-next a') == None:
                self.logger.info("no more pages")
            else:
                next_page = soup.select_one('main.content > div > ul > li.pagination-next a').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('main.content > article > div.entry-content img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('main.content > article > div.entry-content p') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item