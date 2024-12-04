

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


class FrancebleuSpider(BaseSpider):
    name = 'francebleu'
    author = '潘宇豪'
    website_id = 2773
    language_id = 1884
    current_day = ''
    begin = False
    start_urls = ['https://www.francebleu.fr']

    @staticmethod
    def get_today_url():
        t = time.localtime()
        year = str(t.tm_year)
        month = str(t.tm_mon) if len(str(t.tm_mon)) == 2 else '0' + str(t.tm_mon)
        day = str(t.tm_mday) if len(str(t.tm_mday)) == 2 else '0' + str(t.tm_mday)
        FrancebleuSpider.current_day = year + '-' + month + '-' + day + ' 00:00:00'
        return 'https://www.francebleu.fr/api/archives/' + year + '-' + month + '-' + day + '/documents?limit=16'

    @staticmethod
    def get_yesterday_url():
        FrancebleuSpider.current_day = OldDateUtil.timestamp_to_datetime_str(
            OldDateUtil.str_datetime_to_timestamp(FrancebleuSpider.current_day) - 86400)
        return 'https://www.francebleu.fr/api/archives/' + FrancebleuSpider.current_day.split(' ')[
            0] + '/documents?limit=16'

    @staticmethod
    def time_fix(time_pre):
        date_pre = time_pre.split(' ')[1]
        time = time_pre.split(' ')[3]
        date = date_pre.split('/')[2] + '-' + date_pre.split('/')[1] + '-' + date_pre.split('/')[0]
        return date + ' ' + time + ':00'

    def parse(self, response):
        if self.begin:
            page_json = response.json()
            next_part = page_json['next']
            news_list = [news for news in page_json['results']]
            for news in news_list:
                detailed_url = 'https://www.francebleu.fr/' + news['path']
                title = news['title']
                abstract = news['standFirst']
                pub_time_pre = news['date']
                if pub_time_pre.split(' ')[0] == 'Le':
                    pub_time = self.time_fix(pub_time_pre)
                else:
                    if 'min' in pub_time_pre:
                        _min = pub_time_pre.split(' ')[-1].strip('min')
                        if int(_min) >= 60:
                            pub_time = self.current_day.split(' ')[0] +' 01:00:00'
                        else:
                            pub_time = self.current_day.split(' ')[0] + ' 00:' + (
                                _min if len(_min) == 2 else '0' + _min) + ':00'
                    else:
                        pub_time = self.current_day.split(' ')[0] + ' ' + pub_time_pre.split(' ')[-1].strip(
                            'h') + ':00:00'
                if pub_time.split(' ')[1] == '24:00:00':
                    pub_time = pub_time.split(' ')[0] + ' 23:59:59'
                response.meta['title'] = title
                response.meta['abstract'] = abstract
                response.meta['pub_time'] = pub_time
                if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(pub_time):
                    yield scrapy.Request(url=detailed_url, callback=self.parse_detailed, meta=response.meta)
                else:
                    return

            if not next_part:
                yesterday_url = self.get_yesterday_url()
                if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(self.current_day):
                    yield scrapy.Request(url=yesterday_url, callback=self.parse)
                else:
                    return
            else:
                yield scrapy.Request(
                    url='https://www.francebleu.fr/api/archives/' + self.current_day.split(' ')[
                        0] + '/documents?limit=16&date=' + self.current_day.split(' ')[0] + '&pageCursor=' + next_part,
                    callback=self.parse)
        else:
            self.begin = True
            yield scrapy.Request(url=self.get_today_url(), callback=self.parse)

    def parse_detailed(self, response):
        page_soup = BeautifulSoup(response.text, 'html.parser')
        category1 = page_soup.findAll('li', attrs={'class': "svelte-1vj0enf"})[-2].text

        images = []
        span = page_soup.find('span', attrs={'itemprop': "caption"})
        if not span:
            return
        image_pre = page_soup.findAll('img', attrs={'alt': span.text})
        for image in image_pre:
            if 'https://' in image['src']:
                images.append(image['src'])

        body = ''
        body_parts_num = 0
        body_pre = page_soup.find('div', attrs={'class': "content-article svelte-6bn6a2"})
        body_parts = body_pre.find('div', attrs={'class': "Body"}).findAll('p')
        if not body_parts:
            return
        for body_part in body_parts:
            body += body_part.text.replace('  ', '').replace('\n', '') + '\n'
            body_parts_num += 1
        if body_parts_num == 1:
            body = response.meta['abstract'].replace('  ', '').replace('\n', '') + '\n' + body
        body.strip('\n')

        item = NewsItem(language_id=self.language_id)
        item['category1'] = category1
        item['pub_time'] = response.meta['pub_time']
        item['body'] = body
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['images'] = images
        yield item

