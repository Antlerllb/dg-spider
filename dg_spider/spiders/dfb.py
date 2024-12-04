# encoding: utf-8
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


class DfbSpider(BaseSpider): # author:田宇甲
    name = 'dfb'
    website_id = 1760
    language_id = 1898
    start_urls = ['https://www.dfb.de/news/page/30/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .news-listing div')[0:30:3]:
            try:  # 有广告
                ssd = i.select_one(' .news-listing-subline').text.split(' // ')[0].strip().split(' ')
                time_ = ssd[0].split('.')[-1] + '-' + ssd[0].split('.')[1] + '-' + ssd[0].split('.')[0] + ' ' + ssd[1] + ':00'
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    meta = {'pub_time_': time_, 'category1_': (i.select_one(' .news-listing-subline').text.split(' // ')[1].strip() if len(i.select_one(' .news-listing-subline').text.split(' // '))>1 else None), 'title_': i.select_one(' .news-listing-headline').text.strip(), 'abstract_': i.select_one(' .news-listing-teaser').text.strip(), 'images_': ('https://www.dfb.de/'+i.a.img['data-src'] if i.a.img is not None else '')}
                    yield Request('https://www.dfb.de/'+i.select_one(' .col-sm-6 a')['href'], callback=self.parse_item, meta=meta)
            except:
                pass
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request('https://www.dfb.de/news/page/'+str(int(response.url.split('page/')[1].strip('/'))+1)+'/')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .articleBodyText.noprint.push-b20').text
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = [response.meta['images_']]
        yield item
  #新闻量
