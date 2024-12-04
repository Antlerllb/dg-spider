


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

# author: robot_2233

class DenaSpider(BaseSpider):
    name = 'dena'
    website_id = 1734
    language_id = 1898
    start_urls = ['https://www.dena.de/newsroom/?tx_solr%5Bfilter%5D%5B0%5D=pagetype_stringS%3AArtikel&tx_solr%5Bfilter%5D%5B1%5D=pagetype_stringS%3AMeldungen&type=1519&tx_solr%5Bpage%5D=1']
    # proxy = '02'
    page = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .loader__target .teaser.teaser--horiz'):
            try: # 有的不是新闻
                ssd = i.select_one(' .teaser__date').text.strip().split('.')
                time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    meat = {'title_': i.a.text.strip(), 'time_': time_, 'abstract_': i.select_one(' .teaser__summary').text.strip(), 'category1_': 'Newsroom'}
                    yield Request('https://www.dena.de/'+i.a['href'], callback=self.parse_item, meta=meat)
            except:
                pass
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            DenaSpider.page += 1
            yield Request('https://www.dena.de/newsroom/?tx_solr%5Bfilter%5D%5B0%5D=pagetype_stringS%3AArtikel&tx_solr%5Bfilter%5D%5B1%5D=pagetype_stringS%3AMeldungen&type=1519&tx_solr%5Bpage%5D='+str(DenaSpider.page))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .ce-text p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = []
        try:
            images_ = soup.select(' .article__body.ce-container img')
            for each in images_:
                images_.append('https://www.dena.de/'+each['srcset'])
        except:
            pass
        yield item
