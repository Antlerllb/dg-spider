import scrapy
import time
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

class DawnnewsSpider(BaseSpider):
    name = 'dawnnews'
    website_id = 2286
    language_id = 2238
    author = '廖信峰'
    start_urls = ['https://www.dawnnews.tv/archive/pakistan']
    current_day = ''
    begin = False

    # 在这里设置下载延迟
    download_delay = 2.5

    @staticmethod
    def get_today_url():
        t = time.localtime()
        year = str(t.tm_year)
        month = str(t.tm_mon) if len(str(t.tm_mon)) == 2 else '0' + str(t.tm_mon)
        day = str(t.tm_mday) if len(str(t.tm_mday)) == 2 else '0' + str(t.tm_mday)
        DawnnewsSpider.current_day = year + '-' + month + '-' + day + ' 00:00:00'
        return 'https://www.dawnnews.tv/archive/pakistan/' + year + '-' + month + '-' + day

    @staticmethod
    def get_yesterday_url(today):
        DawnnewsSpider.current_day = OldDateUtil.timestamp_to_datetime_str(
            OldDateUtil.str_datetime_to_timestamp(today) - 86400)
        return 'https://www.dawnnews.tv/archive/pakistan/' + DawnnewsSpider.current_day.split(' ')[0]

    def parse(self, response):
        if self.begin:
            soup = BeautifulSoup(response.text, 'lxml')
            news_list = soup.find('div', attrs={'class': 'bg-white text-black'}).findAll('article')
            url_list = []
            for i in news_list:
                url_list.append(i.find('h2').find('a').get('href'))
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
        soup = BeautifulSoup(response.text, 'lxml')
        images = [soup.find('div', class_='media__item').find('img').get('src')]
        title = soup.find('a', class_='story__link').text
        abstract = soup.find('div', class_='story__content').find('p').text

        body = ''
        for i in soup.find('div', class_='story__content').findAll('p'):
            body += i.text + '\n\n'  # 在每个段落的末尾添加两个换行符来分隔段落

        category1 = soup.find('a', class_='story__link').text

        item = NewsItem(language_id=self.language_id)
        item['category1'] = category1
        item['pub_time'] = response.meta['pub_time']
        item['body'] = body
        item['title'] = title
        item['abstract'] = abstract
        item['images'] = images
        yield item
