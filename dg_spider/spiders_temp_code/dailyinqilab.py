from scrapy import Selector




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

# author : 王晋麟
class DailyinqilabSpider(BaseSpider):
    name = 'dailyinqilab'
    website_id = 2263
    language_id = 1779
    start_urls = ['https://dailyinqilab.com/']
    transform = {
        '০': '0',
        '১': '1',
        '২': '2',
        '৩': '3',
        '৪': '4',
        '৫': '5',
        '৬': '6',
        '৭': '7',
        '৮': '8',
        '৯': '9',
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
        'ডিসেম্বর': '12'
    }

    def time_transform(self, string, mode):
        if mode == 1:
            return ''.join([self.transform[string[i]] for i in range(len(string))])
        elif mode == 2:
            return self.transform[string]

    def parse(self, response):
        # OldDateUtil.time = OldDateUtil.time_ago(day=3)
        sel = Selector(response)
        li_lists = sel.css('.navbar-nav li')
        tps = []
        in_page_tps = []
        for li in li_lists[1:]:
            tps.append((li.css('a::attr(href)').get(), li.css('a::text').get()))
            in_page_tps = [tp for tp in tps if tp[0] != '#']
        for href, category2 in in_page_tps:
            yield Request(url=href, callback=self.parse_page, meta={'category2': category2})

    def parse_page(self, response):
        sel = Selector(response)
        flag = True
        for news in sel.css('.mt-5 > .col-md-6'):
            time = news.css('.news-date-time::text').get().replace(',', '').strip().split(' ')
            pub_time = '{}-{}-{} {}:{}:00'.format(self.time_transform(time[2], 1), self.time_transform(time[1], 2),
                                                  self.time_transform(time[0], 1),
                                                  self.time_transform(time[3].split(':')[0], 1),
                                                  self.time_transform(time[3].split(':')[1], 1))
            if OldDateUtil.time is None or OldDateUtil.time <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                news_href = news.css('a::attr(href)').get()
                try:
                    title = news.css('.content-heading::text').get().strip()
                except:
                    title = ''
                yield Request(url=news_href, callback=self.parse_item, meta={'category2': response.meta['category2'],
                                                                             'title': title,
                                                                             'pub_time': pub_time})
            else:
                flag = False
                break
        try:
            if flag:
                next_page_url = sel.css('.pagination a[rel="next"]::attr(href)').get()
                yield Request(url=next_page_url, callback=self.parse_page, meta={'category2': response.meta['category2']})
        except:
            pass

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        sel = Selector(response)
        item = NewsItem(language_id=self.language_id)
        item['category1'] = 'সংবাদ'
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title'] if response.meta['title'] != '' else sel.css('.col-md-9 h2::text').get().strip()
        item['pub_time'] = response.meta['pub_time']
        try:
            item['images'] = [img.css('img::attr(src)').get() for img in sel.css('.col-md-9 .new-details img')]
        except:
            item['images'] = None
        item['body'] = '\n'.join([content.text.strip() for content in soup.select('.col-md-9 .new-details .description p') if content.text.strip() != ''])
        item['abstract'] = item['body'].split('\n')[0] if item['body'].split('\n')[0] != '' else item['body'].strip().split('।')[0]
        yield item

