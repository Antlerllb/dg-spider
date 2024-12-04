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
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# 该网站有反爬机制，访问过快会被封IP
# author: 王晋麟
# check:lzl
class trabajadoresSpider(BaseSpider):
    name = 'trabajadores'
    website_id = 1296
    language_id = 2181
    start_urls = ['https://www.trabajadores.cu/']
    custom_settings = {'RETRY_TIMES': 100, 'DOWNLOAD_DELAY': 3, 'RANDOMIZE_DOWNLOAD_DELAY': True}

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for category in soup.select('#menu-menu-principal > li')[1:9]:
            category2 = category.select('a')[0].text
            in_page_url = category.select('a')[0].attrs['href']
            yield Request(url=in_page_url, callback=self.parse_news, meta={'category2': category2})


    def parse_news(self, response):
        flag = True
        soup = BeautifulSoup(response.text, "html.parser")
        for news in soup.select('.loop article'):
            time = news.select('header time')[0].attrs['datetime'].split('T')
            pub_time = time[0] + ' ' + time[1].split('+')[0]  # pub_time
            if OldDateUtil.time is None or int(OldDateUtil.time) <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                title = news.select('header h3 a')[0].text.strip()  # title
                try:
                    abstract = news.select('.entry-summary p')[0].text.strip()  # abstract
                except:
                    abstract = ''
                yield Request(url=news.select('header h3 a')[0].attrs['href'], callback=self.parse_item, meta={ 'category2': response.meta['category2'], 'pub_time': pub_time, 'title': title, 'abstract': abstract})
            else:
                self.logger.info("时间截止")
                flag = False
                break
        if flag:
            try:
                next_page_url = soup.select('.nextpostslink')[0].attrs['href']
                if(next_page_url != '#'):
                    yield Request(url=next_page_url, callback=self.parse_news, meta={'category2': response.meta['category2']})
                else:
                    pass
            except:
                pass


    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = 'news'
        item['category2'] = response.meta['category2']
        item['body'] = ' '.join([context.text.strip() for context in soup.select('div[itemprop="text"] p')])  # body
        item['abstract'] = response.meta['abstract'] if response.meta['abstract'] != '' else item['body'].split('.')[0]
        item['pub_time'] = response.meta['pub_time']
        try:
            item['images'] = [image.attrs['data-src'] for image in soup.select('div[itemprop="text"] img')]
        except:
            item['images'] = []
        yield item


