# encoding: utf-8
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil





class indonesianSpiderSpider(BaseSpider):
    name='indonesian'
    website_id=73
    language_id=1866
    start_urls = ['https://indonesian.cri.cn/china/index.shtml?spm=C77783.PVuqMaJp1sU3.EBh5xqK9Mj8L.11', 'https://indonesian.cri.cn/china_asean/index.shtml?spm=C77783.PVuqMaJp1sU3.EBh5xqK9Mj8L.33', 'https://indonesian.cri.cn/world/index.shtml?spm=C77783.PVuqMaJp1sU3.EBh5xqK9Mj8L.22']  # author:田宇甲 挑战最短爬虫行数，我喂自己袋盐

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .text_list li'):
            meta = {'pub_time_': i.select_one(' .time').text+' 00:00:00', 'title_': i.a.text, 'category1_': response.url.split('/index')[0].split('.cn/')[1]}
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(i.select_one(' .time').text + ' 00:00:00') >= int(OldDateUtil.time):
                yield scrapy.http.request.Request(i.a['href'], callback=self.parse_item, meta=meta)

    def parse_item(self, response):
        soup, item = BeautifulSoup(response.text, 'html.parser'), NewsItem()
        item['pub_time'], item['category1'], item['category2'], item['title'], item['body'], item['abstract'], item['images'] = response.meta['pub_time_'], response.meta['category1_'], None, response.meta['title_'], soup.select_one(' #abody').text.strip('\n'), soup.select_one(' #abody').text.strip('\n').split('\n')[0], (soup.select_one(' #abody').img['src'] if soup.select_one(' #abody').img is not None else None).replace('//', 'https://') if (soup.select_one(' #abody').img['src'] if soup.select_one(' #abody').img is not None else None) is not None and 'http' not in (soup.select_one(' #abody').img['src'] if soup.select_one(' #abody').img is not None else None) else (soup.select_one(' #abody').img['src'] if soup.select_one(' #abody').img is not None else None)
        yield item
