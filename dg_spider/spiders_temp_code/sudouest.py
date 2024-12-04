

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class SudouestSpider(BaseSpider):
    name = 'sudouest'
    author = '潘宇豪'
    website_id = 2768
    language_id = 1884
    current_day = ''
    begin = False
    ifover = False
    start_urls = ['https://www.sudouest.fr/articles']

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
        SudouestSpider.current_day = year + '-' + month + '-' + day + ' 00:00:00'
        return 'https://www.sudouest.fr/articles/' + year + '/' + day + '-' + month + '-' + year

    @staticmethod
    def get_yesterday_url(today):
        SudouestSpider.current_day = OldDateUtil.timestamp_to_datetime_str(
            OldDateUtil.str_datetime_to_timestamp(today) - 86400)
        yesterday = SudouestSpider.current_day.split(' ')[0]
        return 'https://www.sudouest.fr/articles/' + yesterday.split('-')[0] + '/' + yesterday.split('-')[2] + '-' + \
            yesterday.split('-')[1] + '-' + yesterday.split('-')[0]

    def parse(self, response):
        if self.begin:
            soup = BeautifulSoup(response.text, 'html.parser')
            li_list = soup.findAll('li', attrs={'class': "base-margin-bottom list-item"})
            url_list = []
            for li in li_list:
                url_list.append('https://www.sudouest.fr/' + li.find('a')['href'])
            for url in url_list:

                yield scrapy.Request(url=url, callback=self.parse_detailed)
            today_url = self.get_yesterday_url(self.current_day)
            if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(self.current_day):
                yield scrapy.Request(url=today_url, callback=self.parse)
            else:
                return
        else:
            self.begin = True
            yield scrapy.Request(url=self.get_today_url(), callback=self.parse)

    def parse_detailed(self, response):
        page_soup = BeautifulSoup(response.text, 'html.parser')
        if page_soup.find('h1', attrs={'class': "page-title"}) == None:
            return
        title = page_soup.find('h1', attrs={'class': "page-title"}).text

        time_class = page_soup.find('div', attrs={'class': 'publishing'})
        if time_class == None:
            return
        pub_time_pre = time_class.find('time')['datetime']
        pub_time = self.time_fix(pub_time_pre)

        _id = response.url.split('.php')[0].split('-')[-1]
        if page_soup.find('span', attrs={'id': str(_id)}) == None:
            return

        image_pre = page_soup.find('figure', attrs={'class': "back-button-target-horizon"})
        if image_pre == None:
            return
        images = [image_pre.find('img')['src']]
        abstract = page_soup.find('span', attrs={'id': str(_id)})
        if abstract == None:
            return
        else:
            abstract = abstract.text

        body = ''
        body_parts = page_soup.findAll('div', attrs={'class': "full-content"})
        if body_parts == []:
            return
        for body_part in body_parts:
            p_tags = body_part.findAll('p')
            for p_tag in p_tags:
                body += p_tag.text
                body += '\n'

        if abstract == '':
            abstract = body.split('\n')[0]
        else:
            body = abstract + '\n' + body
        body = body.strip('\n')

        topics = page_soup.find('div', attrs={'class': "breadcrumb"})
        category_pre = topics.findAll('a')
        if category_pre != []:
            category1 = category_pre[-1].text
        else:
            return

        item = NewsItem(language_id=self.language_id)
        item['category1'] = category1
        item['pub_time'] = pub_time
        item['body'] = body
        item['title'] = title
        item['abstract'] = abstract
        item['images'] = images
        yield item




