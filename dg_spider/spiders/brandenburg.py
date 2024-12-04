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

# check:wpf pass


class BrandenburgSpider(BaseSpider):  # author：田宇甲
    name = 'brandenburg'
    website_id = 1698
    language_id = 1898
    start_urls = ['https://msgiv.brandenburg.de/msgiv/de/presse/pressemitteilungen/?skip30488=0']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .columns.text-justify-xx .trennung.medium-12.m2-press-bottom-space'):
            ssd = i.select_one(' .bb-teaser-meta').text.strip().split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_, 'title_': i.h3.text.strip().strip('\n'), 'category1_': 'pressemitteilungen', 'images_': []}
                yield Request('https://msgiv.brandenburg.de'+i.a['href'], callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request(response.url.replace('skip30488=' + response.url.split('skip30488=')[1], 'skip30488=' + str(int(response.url.split('skip30488=')[1]) + 20)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .bb-text-justify-xx p')])
        item['abstract'] = soup.select(' .bb-text-justify-xx p')[0].text
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
