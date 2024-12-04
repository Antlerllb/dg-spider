import re
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
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


class LadeshSpider(BaseSpider):
    name = 'ladesh'
    website_id = 2256
    language_id = 1779
    author = '李杭'
    start_urls = ['https://www.webbangladesh.com/page/1/?s']
    page_num = 1144
    this_page = 1

    @staticmethod
    def time_fix(time):
        year = time.split()[-1]
        month = time.split()[0]
        date = time.split()[1].replace(',', '')

        month = OldDateUtil.EN_1866_DATE[month]

        if month >= 10:
            month = str(month)
        else:
            month = '0' + str(month)

        if len(date) == 1:
            date = '0' + date

        return year + '-' + month + '-' + date + ' 00:00:00'

    def parse(self, response):
        # print(response.url)
        soup = BeautifulSoup(response.text, 'lxml')
        news_list = soup.findAll('div', attrs={'class': 'postlayouts'})
        pub_time_last = ''
        for i in news_list:
            time = i.find('div', attrs={'class': 'post-date'})
            if not time:
                continue
            pub_time = self.time_fix(time.text)
            pub_time_last = pub_time
            if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(pub_time):
                url = i.find('a')['href']
                title = i.find('a').text
                abstract = i.find('div', attrs={'class': 'entry-summary'}).find('p').text.replace('…', '')
                response.meta['pub_time'] = pub_time
                response.meta['title'] = title
                response.meta['abstract'] = abstract
                yield scrapy.Request(url=url, callback=self.parse_detial, meta=response.meta)

        if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(pub_time_last):
            if self.this_page < self.page_num:
                self.this_page += 1
                # print('thispage:' + str(self.this_page))
                yield scrapy.Request(url='https://www.webbangladesh.com/page/'+str(self.this_page) + '/?s',
                                     callback=self.parse)
            else:
                return
        else:
            return

    def parse_detial(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        category1 = 'no category'

        body=''
        body_parts = soup.find('div',attrs={'class': 'entry-content'}).findAll('p')
        # body_parts = response.xpath('/html/body/div[3]/div[1]/div[1]/article/div/p')
        if not body_parts:
            return
        for body_part in body_parts:
            body += body_part.text
            body += '\n'
        body.strip('\n')

        images = [soup.find('div',attrs={'class': 'post-thumb'}).find('img')['src']]

        item = NewsItem(language_id=self.language_id)
        item['category1'] = category1
        item['pub_time'] = response.meta['pub_time']
        item['body'] = body
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['images'] = images
        yield item

