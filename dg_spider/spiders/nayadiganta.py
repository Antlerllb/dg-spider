import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


from scrapy import Selector
# from fastapi.responses import HTMLResponse

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


class NayadigantaSpider(BaseSpider):
    name = 'nayadiganta'
    website_id = 2244
    language_id = 1779
    author = '李杭'
    start_urls = ['https://www.dailynayadiganta.com/archive']
    current_day = ''
    begin = False

    @staticmethod
    def get_today_url():
        t = time.localtime()
        year = str(t.tm_year)
        month = str(t.tm_mon) if len(str(t.tm_mon)) == 2 else '0' + str(t.tm_mon)
        day = str(t.tm_mday) if len(str(t.tm_mday)) == 2 else '0' + str(t.tm_mday)
        NayadigantaSpider.current_day = year + '-' + month + '-' + day + ' 00:00:00'
        return 'https://www.dailynayadiganta.com/archive/' + year + '-' + month + '-' + day

    @staticmethod
    def get_yesterday_url(today):
        NayadigantaSpider.current_day = OldDateUtil.timestamp_to_datetime_str(
            OldDateUtil.str_datetime_to_timestamp(today) - 86400)
        return 'https://www.dailynayadiganta.com/archive/' + NayadigantaSpider.current_day.split(' ')[0]

    def parse(self, response):
        if self.begin:
            soup = BeautifulSoup(response.text, 'lxml')
            news_list = soup.find('ol', attrs={'class': 'margin archive-news-list'}).findAll('li')
            url_list = []
            for i in news_list:
                url_list.append(i.find('a')['href'])
            for url in url_list:
                pub_time = response.url.split('/')[-1] + ' 00:00:00'
                response.meta['pub_time'] = pub_time
                yield scrapy.Request(url=url, callback=self.parse_detail, meta=response.meta)
            today_url = self.get_yesterday_url(self.current_day)
            if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(self.current_day):
                yield scrapy.Request(url=today_url, callback=self.parse)
            else:
                return
        else:
            self.begin = True
            yield scrapy.Request(url=self.get_today_url(), callback=self.parse)

    def parse_detail(self, response):
        # print(response.text)
        soup = BeautifulSoup(response.text, 'lxml')
        images = [soup.find('div', attrs={'class': 'image-holder margin-bottom-10'}).find('img')['src']]
        title = soup.find('header', attrs={'class': 'headline-header margin-bottom-10'}).text

        # body = ''
        #
        # body_parts = soup.findAll('p', attrs={'style': 'text-align: justify;'})
        # for body_part in body_parts:
        #     body += body_part.text.replace('\n', '')
        #     body += '\n'
        # body = body.strip('\n')
        # print(body)

        # abstract = body.split('\n')[0]

        body = soup.find('div', attrs={'class': 'news-content'}).text.replace('\n\n', '')[1:]
        abstract = body.split('\n')[0]
        body.strip('\n')


        category1 = soup.find('ol', attrs={'class': 'breadcrumb'}).findAll('li')[1].text

        item = NewsItem(language_id=self.language_id)
        item['category1'] = category1
        item['pub_time'] = response.meta['pub_time']
        item['body'] = body
        item['title'] = title
        item['abstract'] = abstract
        item['images'] = images
        yield item

