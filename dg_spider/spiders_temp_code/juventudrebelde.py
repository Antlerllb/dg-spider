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
class juventudrebeldeSpider(BaseSpider):
    name = 'juventudrebelde'
    website_id = 1288
    language_id = 2181
    start_urls = ['https://www.juventudrebelde.cu/']
    custom_settings = {'RETRY_TIMES': 100, 'DOWNLOAD_DELAY': 1, 'RANDOMIZE_DOWNLOAD_DELAY': True}   # 下载延时设置为1，因为爬太快可能会被反爬
    proxy = '02'
    page = 1
    month = {
        'enero': '1',
        'febrero': '2',
        'marzo': '3',
        'abril': '4',
        'mayo': '5',
        'junio': '6',
        'julio': '7',
        'agosto': '8',
        'septiembre': '9',
        'octubre': '10',
        'noviembre': '11',
        'diciembre': '12'
    }

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category2 = soup.select('#items_submenu li a')[1].text
        in_page_url = soup.select('#items_submenu li a')[1].attrs['href']
        yield Request(url=in_page_url, callback=self.parse_news, meta={'category2': category2})


    def parse_news(self, response):
        flag = True
        count = 1   # 新闻页格式太差，解决特殊情况
        soup = BeautifulSoup(response.text, "html.parser")
        try:   # 页面格式不规范，selector路径可能不一致，此处选择跳过
            for news in soup.select('#search_paginate div.row'):
                time = news.select('div .search-first-result')[0].text.split(' ')
                pub_time = time[3] + '-' + self.month[time[2]] + '-' + time[1] + ' ' + time[5]   # pub_time
                if OldDateUtil.time is None or int(OldDateUtil.time) <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                    count += 1
                    title = news.select(".search-third-result a h3")[0].text
                    try:
                        abstract = ' '.join([content.text.strip() for content in news.select('.search-third-result p')])
                    except:
                        abstract = ' '
                    if len(abstract) > 5000:   # 有一个恶心的特殊情况：下面的新闻可能错误地放在了某一个新闻的概要里
                        abstract = ' '
                    news_url = news.select(".search-third-result a")[0].attrs["href"]
                    yield Request(url=news_url, callback=self.parse_item, meta={'category2': response.meta['category2'], 'pub_time': pub_time, 'title': title, 'abstract': abstract})
                else:
                    self.logger.info("时间截止")
                    flag = False
                    break
                if count > 10:   # 每页最多只有10篇新闻
                    break
        except:
            pass
        if flag:
            self.page += 1
            yield Request(url=f'https://www.juventudrebelde.cu/noticias?page={self.page}', callback=self.parse_news, meta={'category2': response.meta['category2']})

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = 'news'
        item['category2'] = response.meta['category2']
        item['body'] = '.'.join([content.text.strip() for content in soup.select('.resize_md article p, .resize_md article h2, .news-content .content p, .news-body p')])
        item['abstract'] = response.meta['abstract'] if response.meta['abstract'] != ' ' else soup.select('#title-news h4 p')[0].text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [image.attrs['src'] for image in soup.select('article img, .news-body img')]
        yield item