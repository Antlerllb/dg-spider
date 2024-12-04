# encoding: utf-8




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

# author: 王晋麟
# check:lzl
class primiciaSpider(BaseSpider):
    name = 'primicia'
    website_id = 1320
    language_id = 2181
    start_urls = ['https://primicia.com.ve/']
    custom_settings = {'RETRY_TIMES': 100, 'DOWNLOAD_DELAY': 0.1, 'RANDOMIZE_DOWNLOAD_DELAY': True}
    proxy = '02'
    month = {
        'enero': '1',
        'febrero': '2',
        'marzo': '3',
        'abril': '4',
        'mayo': '5',
        'junio': '6',
        'julio': '7',
        'agosto': '8',
        'septiembre': '9',
        'octubre': '10',
        'noviembre': '11',
        'diciembre': '12'
    }

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for category in soup.select('#menu-top-menu > li')[1:13]:
            category1 = category.select('a')[0].text
            page_url = category.select('a')[0].attrs['href']
            yield Request(url=page_url, callback=self.parse_news, meta={'category1': category1})


    def parse_news(self, response):
        flag = True
        soup = BeautifulSoup(response.text, "html.parser")
        for news in soup.select('.col-xl-8 div a.card'):
            time = news.select('.card-footer')[0].text.strip().split(' ')
            pub_time = time[3] + '-' + self.month[time[2]] + '-' + time[1] + ' 00:00:00'
            if OldDateUtil.time is None or int(OldDateUtil.time) <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                title = news.select('.card-body h5')[0].text.strip()   # title
                try:
                    abstract = ''.join([content.text.strip() for content in news.select('.card-body p')])   # abstract
                except:
                    abstract = ''
                news_url = news.attrs["href"]
                yield Request(url=news_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'pub_time': pub_time, 'title': title, 'abstract': abstract})
            else:
                self.logger.info("时间截止")
                flag = False
                break
        if flag:
            try:
                yield Request(url=soup.select('.justify-content-center .next')[0].attrs['href'], callback=self.parse_news, meta={'category1': response.meta['category1']})
            except:
                pass


    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = 'news' if item['category1'] == soup.select('.col-xl-8 a small strong')[0].text.strip() else soup.select('.col-xl-8 a small strong')[0].text.strip()
        item['body'] = ' '.join([content.text.strip() for content in soup.select('.col-xl-8 .text-justify p, .col-xl-8 .text-justify h3')])
        try:
            item['abstract'] = response.meta['abstract'] if response.meta['abstract'] != '' else soup.select('.col-xl-8 .summary')[0].text.strip()
        except:
            item['abstract'] = item['body'].split('.')[0]
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [image.attrs['src'] for image in soup.select('.col-xl-8 .img-fluid, #imgopinion')]
        yield item