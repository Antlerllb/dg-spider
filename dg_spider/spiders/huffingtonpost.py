from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


# check:魏芃枫 pass
class HuffingtonpostSpider(BaseSpider):  # author：田宇甲
    name = 'huffingtonpost'
    website_id = 1774
    language_id = 1898
    start_urls = [f'https://www.huffpost.com/{i}/' for i in ['section/huffpost-personal', 'news', 'news/politics', 'entertainment']]
    # proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .card.card--standard.js-card'):
            meta = {'title_': i.select_one(' .card__headlines').text.strip(), 'category1_': response.url.split('com/')[1].split('/')[0], 'abstract_': i.select_one(' .card__description').text, 'images_': [i.select_one(' .card__image picture source')['srcset']]}
            yield Request(i.a['href'], callback=self.check_check, meta=meta)
        if 'page' not in response.url:
            yield Request(response.url+'?page=2')
        else:
            yield Request(response.url.split('page=')[0]+'page='+str(int(response.url.split('page=')[1])+1))

    def check_check(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        time_ = str(soup.select_one(' .timestamp time')).split('datetime="')[1].split('"')[0].replace('T', ' ').split('-0400')[0]
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.meta['title_']
            item['category1'] = response.meta['category1_']
            item['category2'] = None
            item['body'] = soup.select_one(' .entry__content-and-right-rail-container').text.strip().strip('\n')
            item['abstract'] = response.meta['abstract_']
            item['pub_time'] = time_
            item['images'] = response.meta['images_']
            yield item

