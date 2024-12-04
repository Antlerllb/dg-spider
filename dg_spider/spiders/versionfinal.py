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
class versionfinalSpider(BaseSpider):
    name = 'versionfinal'
    website_id = 1319
    language_id = 2181
    start_urls = ['https://versionfinal.com.ve/']
    custom_settings = {'RETRY_TIMES': 100, 'DOWNLOAD_DELAY': 1, 'RANDOMIZE_DOWNLOAD_DELAY': True}
    proxy = '02'


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for category in soup.select('#main-navigation li')[0:12]:
            category2 = category.select('a')[0].text
            page_url = category.select('a')[0].attrs['href']
            yield Request(url=page_url, callback=self.parse_news, meta={'category2': category2})


    def parse_news(self, response):
        flag = True
        soup = BeautifulSoup(response.text, "html.parser")
        for news in soup.select('.listing-blog article'):
            time = news.select('.post-meta time')[0].attrs['datetime'].split('T')
            pub_time = time[0] + ' ' + time[1].split('-')[0]   # pub_time
            if OldDateUtil.time is None or int(OldDateUtil.time) <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                title = news.select('.title a')[0].text.strip()   # title
                try:
                    abstract = news.select('.post-summary')[0].text.strip()   # abstract
                except:
                    abstract = ''
                news_url = news.select('.title a')[0].attrs["href"]
                yield Request(url=news_url, callback=self.parse_item, meta={'category2': response.meta['category2'], 'pub_time': pub_time, 'title': title, 'abstract': abstract})
            else:
                self.logger.info("时间截止")
                flag = False
                break
        if flag:
            try:
                yield Request(url=soup.select('.bs-numbered-pagination .next')[0].attrs['href'], callback=self.parse_news, meta={'category2': response.meta['category2']})
            except:
                pass


    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = 'news'
        item['category2'] = response.meta['category2']
        item['body'] = ' '.join([content.text.strip() for content in soup.select('.continue-reading-content p')])
        try:
            item['abstract'] = response.meta['abstract'] if response.meta['abstract'] != '' else soup.select('.single-post-excerpt')[0].text.strip()
        except:
            item['abstract'] = item['body'].split('.')[0]
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [image.attrs['src'] for image in soup.select('.single-container article img')]
        yield item