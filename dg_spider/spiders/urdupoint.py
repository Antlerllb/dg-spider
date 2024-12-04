# encoding: utf-8




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
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

# author: 王晋麟
# check:lzl
class urdupointSpider(BaseSpider):
    name = 'urdupoint'
    website_id = 1949
    language_id = 2238
    start_urls = ['https://www.urdupoint.com/']
    custom_settings = {'RETRY_TIMES': 10, 'DOWNLOAD_DELAY': 0.1, 'RANDOMIZE_DOWNLOAD_DELAY': True}
    proxy = '02'
    flag = True
    last_page_number = 0
    category2 = ''

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        page_url = soup.select('.main_nav li:nth-child(15) a')[0].attrs['href']
        category1 = soup.select('.main_nav li:nth-child(15) a')[0].text.strip()  # category1
        yield Request(url=page_url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        in_page_url = soup.select('#main_content div div:nth-child(6) div a.pad5')[0].attrs['href']
        yield Request(url=in_page_url, callback=self.parse_in_page, meta={'category1': response.meta['category1']})

    def parse_in_page(self, response):
        flag2 = True
        soup = BeautifulSoup(response.text, 'html.parser')
        if self.flag:   # 一次就好
            self.last_page_number = soup.select('.pagination [title="Last Page"]')[0].attrs['href'].split('/')[-1].split('.')[0]
            self.category2 = soup.select('.main_bar h2.urdu')[0].text.strip()  # category2
            self.flag = False
            yield Request(url=soup.select('.pagination [title="Next Page"]')[0].attrs['href'], callback=self.parse_in_page, meta={'category1': response.meta['category1'], 'category2': self.category2})
        else:
            for news in soup.select('li.item_shadow'):
                pub_time = news.select('a p span')[0].text.strip() + ' 00:00:00'  # pub_time
                if OldDateUtil.time is None or int(OldDateUtil.time) <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                    title = news.select('a h3')[0].text.strip()  # title
                    news_url = news.select('a')[0].attrs['href']
                    yield Request(url=news_url, callback=self.parse_item, meta={'title': title, 'pub_time': pub_time, 'category1': response.meta['category1'], 'category2': response.meta['category2']})
                else:
                    self.logger.info("时间截止")
                    flag2 = False
                    break
            if flag2:
                next_page_url = soup.select('.pagination [title="Next Page"]')[0].attrs['href']
                next_page_number = next_page_url.split('/')[-1].split('.')[0]
                if int(next_page_number) <= int(self.last_page_number):
                    yield Request(url=next_page_url, callback=self.parse_in_page,meta={'category1': response.meta['category1'], 'category2': response.meta['category2']})

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = '\n'.join(news.text.strip().replace('\n', '') for news in soup.select('#main_content .main_bar .news_article span'))
        item['abstract'] = item['body'].split('    ')[0]
        item['pub_time'] = response.meta['pub_time']
        try:
            item['images'] = [images.attrs['data-src'] for images in soup.select('#main_content .main_bar .news_article span figure img')]
        except:
            item['images'] = []
        yield item