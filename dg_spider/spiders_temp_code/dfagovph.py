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

import re


ENGLISH_MONTH = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'}

# check: 魏芃枫

class dfaSpiderSpider(BaseSpider):
    name = 'dfagovph'
    website_id = 1262
    language_id = 1866
    start_urls = ['https://dfa.gov.ph/'+i for i in ['dfa-news/dfa-releasesupdate?start=0', 'dfa-news/statements-and-advisoriesupdate?start=0', 'dfa-news/news-from-our-foreign-service-postsupdate?start=0']]
    page = 0

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.find_all(class_=re.compile('cat-list-row')):
            ssd = i.select_one(' .list-date.small').text.strip().split('|')[-1].split()
            time_ = ssd[-1] + '-' + OldDateUtil.EN_1866_DATE[ssd[1]] + '-' + str(ssd[0]) + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_, 'title_': i.select_one(' .list-title').text, 'category1_': response.url.split('dfa-news/')[1].split('?')[0]}
                yield Request(url='https://dfa.gov.ph'+i.a.get('href'), callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request(response.url.replace(response.url.split('start=')[1], str(int(response.url.split('start=')[1])+1)))


    def parse_item(self, response):
        soup=BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.find_all(itemprop="articleBody")[0].text
        item['abstract'] = soup.find_all(itemprop="articleBody")[0].text.split('\n')[1]
        item['pub_time'] = response.meta['pub_time_']
        # item['images'] = 'https://dfa.gov.ph'+soup.select_one(' .item-page div img').get('src')
        item['images'] = ['https://dfa.gov.ph' + i for i in
                          response.xpath('//div[@itemprop="articleBody"]//img/@src').getall()]
        yield item
