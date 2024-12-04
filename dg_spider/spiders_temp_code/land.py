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

German_month = {
    'Januar': '01',
    'Februar': '02',
    'März': '03',
    'April': '04',
    'Mai': '05',
    'Juni': '06',
    'Juli': '07',
    'August': '08',
    'September': '09',
    'Oktober': '10',
    'November': '11',
    'Dezember': '12'
}

class LandSpider(BaseSpider):  # author：田宇甲
    name = 'land'
    website_id = 1704
    language_id = 1898
    start_urls = ['https://www.land.nrw/pressemitteilungen?search=&sort_by=combined_date&start_date=&end_date=&items_per_page=30&sort_order=DESC&page=0']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .press-release-list-four-col article'):
            try:
                ssd = i.select_one(' .content-teaser__meta-item').text.split(' ')
                time_ = ssd[-1]+'-'+German_month[ssd[1]]+'-'+ssd[0].strip('.') + ' 00:00:00'
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    meta = {'pub_time_': time_, 'title_': i.h3.text.strip().strip('\n'), 'category1_': 'pressemitteilungen', 'abstract_': i.select_one(' .content-teaser__text').text.strip().strip('\n'), 'images_': ['https://www.land.nrw/'+i.picture.img['src']]}
                    yield Request('https://www.land.nrw/'+i.h3.a['href'], callback=self.parse_item, meta=meta)
            except:  # 有的新闻没有时间，点进去是下载的文档
                pass
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request(response.url.replace('&page=' + response.url.split('&page=')[1], '&page=' + str(int(response.url.split('&page=')[1]) + 1)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .basic-page-template__preface.u-max-width .text  p ')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
