# encoding: utf-8




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

# author: 王晋麟
# check:lzl
class acnSpider(BaseSpider):
    name = 'acn'
    website_id = 2088
    language_id = 2181
    start_urls = ['http://www.acn.cu/']
    base_url = 'http://www.acn.cu'
    custom_settings = {'RETRY_TIMES': 10, 'DOWNLOAD_DELAY': 0.1, 'RANDOMIZE_DOWNLOAD_DELAY': True}
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for category in soup.select('.navbar-nav .dropdown-toggle'):
            category2 = category.text.strip()
            in_page_url = self.start_urls[0] + category.attrs['href']
            yield Request(url=in_page_url, callback=self.parse_news, meta={'category2': category2})


    def parse_news(self, response):
        flag = True
        soup = BeautifulSoup(response.text, "html.parser")
        for news in soup.select('article'):
            time = news.select('.article-aside time')[0].attrs['datetime'].split('T')
            pub_time = time[0] + ' ' + time[1].split('-')[0]  # pub_time
            if OldDateUtil.time is None or int(OldDateUtil.time) <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                title = news.select('.article-header h2 a')[0].text.strip()  # title
                news_url = self.start_urls[0] + news.select('.article-header h2 a')[0].attrs['href']
                try:
                    abstract = news.select('.article-intro p')[0].text  # abstract
                except:
                    abstract = ''
                yield Request(url= news_url, callback=self.parse_item, meta={ 'category2': response.meta['category2'], 'pub_time': pub_time, 'title': title, 'abstract': abstract})
            else:
                self.logger.info("时间截止")
                flag = False
                break
        if flag:
            try:
                yield Request(url=self.base_url + soup.select('a[title="Siguiente"]')[0].attrs['href'], callback=self.parse_news, meta={'category2': response.meta['category2']})
            except:
                pass

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = 'news'
        item['category2'] = response.meta['category2']
        item['body'] = ' '.join([news.text.strip() for news in soup.select('.article-content p')])   # body
        item['abstract'] = item['body'].split('.')[0] if response.meta['abstract'] == '' else response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        try:
            item['images'] = [self.base_url + image.attrs['src'].replace('http://www.acn.cu', '') for image in soup.select('.article-content img')]
        except:
            item['images'] = []
        yield item