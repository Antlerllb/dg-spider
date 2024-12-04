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

import re


ENGLISH_MONTH = {
        'জানুয়ারি': '01',
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
        'ডিসেম্বর': '12'}



#author:黄锦荣
# check：凌敏 pass
class protipokkhoSpider(BaseSpider):
    name = 'protipokkho'
    website_id = 1909
    language_id = 1779
    start_urls = [
        'https://protipokkho.com/category/writer',
        'https://protipokkho.com/category/amader-kotha/'
                  ]
    page = 0
    # is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        # for i in soup.select('  section div article'):
        article_list = response.xpath('//*[@id="contentbx_grace_news"]/section/div/div')
        for i in article_list:
            time = i.xpath('.//div[@class="post-date"]/text()').get().replace(',', ' ').split(' ')
            # print(time)
            year = "2020"
            month = OldDateUtil.EN_1866_DATE[time[0]]
            day = "12"
            time_ =  year+'-'+month+'-'+day+' 00:00:00'
            title_ =response.xpath('//header/h3/a/text()').get()
            # print(title_)
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_':time_,'title_':title_,'category1_': response.url.split('category/')[1].split('/')[0]}
                # print(response.url)
                yield Request(url=i.xpath('.//a[@class="blogreadmore"]/@href').get(), callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            if 'page' not in response.url:
                yield Request(response.url + '/page/2', callback=self.parse, meta=meta)
            else:
                # print(response.url)
                yield Request(response.url.replace(response.url.split('page/')[1].split('/')[0],
                                               str(int(response.url.split('page/')[1].split('/')[0]) + 1)),
                                 callback=self.parse, meta=response.meta)


    def parse_item(self, response):
        soup=BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        # item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div/p/text()')])
        item['body'] = response.xpath('//div/p/text()').get()
        item['abstract'] = response.xpath('//div/p/text()').get()
        item['pub_time'] = response.meta['pub_time_']
        try:
            img = response.xpath('//div/figure/img/@src').get().split(',')[0]
            item['images'] = img
        except:
            item['images'] = []
        yield item