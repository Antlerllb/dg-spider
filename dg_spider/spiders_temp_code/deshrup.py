import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



class DeshrupSpider(BaseSpider):
    name = 'deshrup'
    author = '潘宇豪'
    website_id = 2264
    language_id = 1779
    start_urls = ['https://www.deshrupantor.com/home/allnews']
    max_page_num = 0
    page_num = 0

    @staticmethod
    def time_fix(time):
        clock = ''
        for i in time:
            if i == ':':
                clock += i
            elif i == 'ও':
                clock += '3'
            else:
                clock += str(OldDateUtil.BN_1779_DATE[i])
        return clock

    def parse(self, response):
        page_soup = BeautifulSoup(response.text, 'html.parser')
        news_list = page_soup.findAll('div', attrs={'class': "all-news-list row"})
        for news in news_list:
            title_pre = news.findAll('a')
            date = news.find('img')['src'].split('/news_images/')[1][:10].replace('/', '-')
            title = title_pre[1].text.replace('\n', '')
            category1 = title_pre[0].text.strip(' | ')
            response.meta['title'] = title
            response.meta['category1'] = category1
            response.meta['date'] = date
            if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(date + ' 00:00:00'):
                yield scrapy.Request(url='https://www.deshrupantor.com/' + title_pre[1]['href'],
                                     callback=self.parse_detailed, meta=response.meta)
            else:
                return
        if not self.max_page_num:
            self.max_page_num = int(
                page_soup.find('div', attrs={'class': "pagination mb-20"}).findAll('a')[-1]['data-ci-pagination-page'])
        if self.page_num < self.max_page_num:
            self.page_num += 1
            yield scrapy.Request(url='https://www.deshrupantor.com/home/allnews/' + str(self.page_num * 20),
                                 callback=self.parse)
        else:
            return

    def parse_detailed(self, response):
        page_soup = BeautifulSoup(response.text, 'html.parser')

        pub_time_pre = page_soup.find('small', attrs={'class': "col-md-8 date"})
        if pub_time_pre.text == '\n':
            pub_time = response.meta['date'] + ' 00:00:00'
        else:
            time = pub_time_pre.text.split(':')[0][-2:] + ':' + pub_time_pre.text.split(':')[1][:2]
            if time[0] not in '০১২':
                return
            pub_time = response.meta['date'] + ' ' + self.time_fix(time) + ':00'

        body = ''
        body_parts_num = 0
        body_pre = page_soup.find('div', attrs={'class': "detailsnews"}).findAll('p')
        if not body_pre:
            return
        for p in body_pre:
            if not p:
                continue
            body += p.text.replace('\n', '')
            body += '\n'
            body_parts_num += 1
        if body_parts_num == 1:
            body = response.meta['title'] + '\n' + body
            abstract = body
        else:
            abstract = body.split('\n')[0]
        body.strip('\n')

        images = ['https://www.deshrupantor.com' + page_soup.find('img', attrs={'class': "main-img"})['src'][1:]]

        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['pub_time'] = pub_time
        item['body'] = body
        item['title'] = response.meta['title']
        item['abstract'] = abstract
        item['images'] = images
        yield item
