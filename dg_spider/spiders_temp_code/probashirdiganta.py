
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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

month = {
         'জানুয়ারী': '01',
         'ফেব্রুয়ারি': '02',
         'মার্চ': '03',
         'এপ্রিল': '04',
         'মে': '05',
         'জুন': '06',
         'জুলাই': '07',
         'আগস্ট': '08',
         'সেপ্টেম্বর': '09',
         'অক্টোবর': '10',
         'নভেম্বর': '11',
         'ডিসেম্বর': '12'
}

day = {
    '১': '01',
    '২': '02',
    '৩': '03',
    '৪': '04',
    '৫': '05',
    '৬': '06',
    '৭': '07',
    '৮': '08',
    '৯': '09',
    '১০': '10',
    '১১': '11',
    '১২': '12',
    '১৩': '13',
    '১৪': '14',
    '১৫': '15',
    '১৬': '16',
    '১৭': '17',
    '১৮': '18',
    '১৯': '19',
    '২০': '20',
    '২১': '21',
    '২২': '22',
    '২৩': '23',
    '২৪': '24',
    '২৫': '25',
    '২৬': '26',
    '২৭': '27',
    '২৮': '28',
    '২৯': '29',
    '৩০': '30',
    '৩১': '31',
}

year = {
    '২০১৪': '2014',
    '২০১৫': '2015',
    '২০১৬': '2016',
    '২০১৭': '2017',
    '২০১৮': '2018',
    '২০১৯': '2019',
    '২০২০': '2020',
    '২০২১': '2021',
    '২০২২': '2022',
    '২০২৩': '2023',
    '২০২৪': '2024',
}
# author : 胡楷
class ProbashirdigantaSpider(BaseSpider):
    name = 'probashirdiganta'
    website_id = 2258
    language_id = 1779
    # allowed_domains = ['']
    start_urls = ['https://www.probashirdiganta.com/']


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories_1 = soup.select('ul.hs-d-bfx > li.nav-item.dropdown > div.dropdown-menu > a')
        categories_2 = soup.select('ul.hs-d-bfx > li.nav-item > a')[6:11]
        for category in categories_1:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
        for category in categories_2:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
    # # #
    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('ul.cat-list-style-one-body > li > a')
        for article in articles:
            article_url = article.get('href')
            yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1']})
        next_ = soup.select_one('ul.pagination > li.next > a')
        if next_ == None:
            pass
        else:
            next_page = next_.get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
    # # #
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        t = soup.select_one('div.post-time > span').text.replace(',', '').split(' ', 6)
        pub_time = year[t[3]] + '-' + month[t[2]] + '-' + day[t[1]] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= OldDateUtil.time:
            item = NewsItem(language_id=self.language_id)
            item['category1'] = response.meta['category1']
            item['category2'] = None
            item['title'] = soup.select_one('div.row h1.post-main-title').text.strip()
            item['pub_time'] = pub_time
            imgs = [img.get('src') for img in soup.select('div.post-main-image > img')]
            if imgs == None:
                item['images'] = None
            else:
                item['images'] = imgs
            item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.post-details > p') if paragraph.text != '' and paragraph.text != ' '])
            item['abstract'] = item['body'].split('\n')[0]
            yield item
        else:
            self.logger.info("时间截止")