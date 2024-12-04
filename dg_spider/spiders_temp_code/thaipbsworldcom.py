from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


# author:武洪艳
class ThaipbsworldcomSpider(BaseSpider):
    name = 'thaipbsworldcom'
    website_id = 1595
    language_id = 1866
    # allowed_domains = ['www.thaipbsworld.com/']
    start_urls = ['https://www.thaipbsworld.com/']  # https://www.thaipbsworld.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories= soup.select('#menu-main-nav > li a')[2:16]
        del categories[7]
        del categories[9]
        for i in categories:
            url= i.get('href')
            yield Request(url=url, callback=self.parse_page, meta={'category1': url.split('/')[-3], 'category2': url.split('/')[-2]})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.grid-box .post-title')
        if OldDateUtil.time is not None:
            t = articles[-1].select_one('.post-tags li:nth-child(1)').text.replace(',', ' ').split(' ')
            last_time = "{}-{}-{}".format(t[3], str(OldDateUtil.EN_1866_DATE[t[0]]).zfill(2), t[1]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            articles = soup.select('div.grid-box .post-title')
            for article in articles:
                tt = article.select_one('.post-tags li:nth-child(1)').text.replace(',', ' ').split(' ')
                pub_time = "{}-{}-{}".format(tt[3], str(OldDateUtil.EN_1866_DATE[tt[0]]).zfill(2), tt[1]) + ' 00:00:00'
                article_url = article.select_one('h2 a').get('href')
                title = article.select_one('h2 a').text
                yield Request(url=article_url, callback=self.parse_item,
                              meta={'category1':  response.meta['category1'], 'category2':  response.meta['category2'] ,'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('div.pagination-box .next.page-numbers') == None:
                self.logger.info("no more pages")
            else:
                next_page = soup.select_one('div.pagination-box .next.page-numbers').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.block-content img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('.block-content') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item
