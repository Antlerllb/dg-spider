

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class LadepecheSpider(BaseSpider):
    name = 'ladepeche'
    author = '潘宇豪'
    website_id = 2766
    language_id = 1884
    current_day = ''
    begin = False
    start_urls = ['https://www.ladepeche.fr/']

    @staticmethod
    def time_fix(time):
        add_hour = int(time.split('+')[1].split(':')[0])
        date = time.split('T')[0] + ' ' + time.split('T')[1].split('+')[0]
        add_num = (8 - add_hour) * 3600
        return OldDateUtil.timestamp_to_datetime_str(OldDateUtil.str_datetime_to_timestamp(date) + add_num)

    @staticmethod
    def get_today_url():
        t = time.localtime()
        year = str(t.tm_year)
        month = str(t.tm_mon) if len(str(t.tm_mon)) == 2 else '0' + str(t.tm_mon)
        day = str(t.tm_mday) if len(str(t.tm_mday)) == 2 else '0' + str(t.tm_mday)
        LadepecheSpider.current_day = year + '-' + month + '-' + day + ' 00:00:00'
        return 'https://www.ladepeche.fr/articles/' + year + '/' + month + '/' + day

    @staticmethod
    def get_yesterday_url(today):
        LadepecheSpider.current_day = OldDateUtil.timestamp_to_datetime_str(
            OldDateUtil.str_datetime_to_timestamp(today) - 86400)
        yesterday = LadepecheSpider.current_day.split(' ')[0]
        return 'https://www.ladepeche.fr/articles/' + yesterday.split('-')[0] + '/' + yesterday.split('-')[1] + '/' + \
            yesterday.split('-')[2]

    def parse(self, response):
        if self.begin:
            page_soup = BeautifulSoup(response.text, 'html.parser')
            category_list = page_soup.findAll('section', attrs={'class': "u-mb-15"})
            today_url = self.get_yesterday_url(self.current_day)
            if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(self.current_day):
                for category in category_list:
                    category_pre = category.find('div', attrs={'class': "archive-day"})
                    category1 = category_pre.find('h2').text
                    if category1 == '\n':
                        continue
                    # print(category1.strip('\n').strip('    '))
                    # print(response.url)
                    response.meta['category1'] = category1.strip('\n').strip('    ')
                    news = category.findAll('li', attrs={'class': "entry-content"})
                    for new in news:
                        title = new.text[2:]
                        response.meta['title'] = title
                        # print('    ' + title)
                        detailed_url = 'https://www.ladepeche.fr/' + new.find('a')['href']
                        # print('    ' + detailed_url)
                        yield scrapy.Request(url=detailed_url, callback=self.parse_detailed, meta=response.meta)
                yield scrapy.Request(url=today_url, callback=self.parse)
            else:
                return
        else:
            self.begin = True
            yield scrapy.Request(url=self.get_today_url(), callback=self.parse)

    def parse_detailed(self, response):
        page_soup = BeautifulSoup(response.text, 'html.parser')

        body_parts_pre = page_soup.find('div',attrs={'class': "article-full__body-content article-paywall p402_premium"})
        if body_parts_pre is None:
            return
        body_parts = body_parts_pre.findAll('p')
        body = ''
        body_parts_num = 0
        for body_part in body_parts:
            body += (body_part.text.replace('  ', '').replace('\n', ''))
            body += '\n'
            body_parts_num += 1
        if body_parts_num == 1:
            body = response.meta['title'] + '\n' + body
        abstract_pre = page_soup.find('p', attrs={'class': "article-full__chapo"})
        if abstract_pre is None:
            abstract = body.split('\n')[1] if body_parts_num == 1 else body.split('\n')[0]
            # 如果body只有一部分，说明换行符前的是title，反之则不是，尽量让abstract优先从body中提取。
        else:
            abstract = abstract_pre.text.replace('  ', '').replace('\n', '').strip("l'essentiel'")
        # print(abstract)
        body.strip('\n')

        pub_time_pre1 = page_soup.find('div', attrs={'class': "article-full__infos-dates"})
        if pub_time_pre1 is None:
            return
        pub_time_pre2 = pub_time_pre1.find('time')['content']
        pub_time = self.time_fix(pub_time_pre2)
        # print(pub_time)

        images_pre = page_soup.find('ul', attrs={'class': "article-full__media-slider"})
        if images_pre is None:
            return
        images = images_pre.find('img', attrs={'class': "responsive-img"})['src']
        # print([images])

        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['pub_time'] = pub_time
        item['body'] = body
        item['title'] = response.meta['title']
        item['abstract'] = abstract
        item['images'] = [images]
        yield item



