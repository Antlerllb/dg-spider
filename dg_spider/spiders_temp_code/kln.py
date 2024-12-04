
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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


# author : 胡楷
class KlnSpider(BaseSpider):
    name = 'kln'
    website_id = 395
    language_id = 2036
    # allowed_domains = ['']
    start_urls = ['https://www.kln.gov.my/']


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('ul.dropdown-menu > li > a')[24:27]
        for category in categories:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
    #
    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('tbody.table-data > tr')
        flag = True
        if OldDateUtil.time is not None:
            tp = articles[-1].select('td.table-cell')[1].text
            tp1 = tp.split('/')
            tp2 = '20' + tp1[2] + '-' + tp1[0] + '-' + tp1[1]
            last_time = tp2.replace(' ', '') + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = article.select_one('td.table-cell > a').get('href')
                tt = article.select('td.table-cell')[1].text
                t1 = tt.split('/')
                t2 = '20' + t1[2] + '-' + t1[0] + '-' + t1[1]
                pub_time = t2.replace(' ', '') + ' 00:00:00'
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            page = soup.select('ul.pager.lfr-pagination-buttons > li > a')
            for a in page:
                if a.text == ' Next ':
                    next_ = a.get('href')
                    if  next_ == "javascript:;":
                        pass
                    else:
                        yield Request(url = next_, callback=self.parse_page, meta=response.meta)
    #
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = None
        title = soup.select_one('div.journal-content-article > p > span > strong')
        if title == None:
            item['title'] = soup.select_one('div.taglib-header > h3.header-title > span').text.strip()
            item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.journal-content-article > a') if paragraph.text != '' and paragraph.text != ' '])
        else:
            item['title'] = title.text.strip()
            item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.journal-content-article > p') if paragraph.text != '' and paragraph.text != ' '])
        if item['body'] == None:
            item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.journal-content-article') if paragraph.text != '' and paragraph.text != ' '])
        item['pub_time'] = response.meta['pub_time']
        item['images'] = None
        item['abstract'] = item['body'].split('\n')[0]
        if item['abstract'] == None:
            item['abstract'] = item['body'].split('\n')[0:3]
        if item['body'] == None:
            pass
        else:
            yield item
    #

