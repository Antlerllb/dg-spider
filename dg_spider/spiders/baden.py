from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# check:wpf pass


class BadenSpider(BaseSpider):  # author：田宇甲
    name = 'baden'
    website_id = 1696
    language_id = 1898
    start_urls = ['https://www.baden-wuerttemberg.de/de/service/presse/pressemitteilungen/?tx_rsmpress_list%5Bpage%5D=1']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .list .list__item'):
            time_ = str(i.time).split('datetime="')[1].split('"')[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_, 'title_': i.h3.text.strip().strip('\n'), 'category1_': 'pressemitteilungen', 'images_': ['https://www.baden-wuerttemberg.de/'+i.img['src']], 'abstract_': i.select_one(' .teaser__text').text.strip()}
                yield Request('https://www.baden-wuerttemberg.de/'+i.a['href'], callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request(response.url.replace('page%5D=' + response.url.split('page%5D=')[1], 'page%5D=' + str(int(response.url.split('page%5D=')[1]) + 1)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .text p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
