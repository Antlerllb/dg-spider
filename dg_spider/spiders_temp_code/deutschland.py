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

class DeutschlandSpider(BaseSpider):  # author：田宇甲
    name = 'deutschland'  # 偶尔有502
    website_id = 1779
    language_id = 1898
    start_urls = ['https://www.deutschland.de/de/news?tid=All&page=0']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .views-infinite-scroll-content-wrapper.clearfix .views-row article'):
            meta = {'title_': i.select_one(' .cover__inner .typoHm').text, 'category1_': 'News', 'abstract_': i.select_one(' .cover__inner .cover__text').text, 'images_': ['https://www.deutschland.de/'+i.picture.img['data-src']]}
            yield Request('https://www.deutschland.de/'+i.select_one(' .cover__image a')['href'], callback=self.check_check, meta=meta)
        yield Request(response.url.split('page=')[0]+'page='+str(int(response.url.split('page=')[1])+1))

    def check_check(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        ssd = soup.select_one(' .story__date').text.strip().split('.') if '/' not in soup.select_one(' .story__date').text else soup.select_one(' .story__date').text.split('/')[1].strip().split('.')
        time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.meta['title_']
            item['category1'] = response.meta['category1_']
            item['category2'] = None
            item['body'] = soup.select_one(' .story__content').text.strip().strip('\n')
            item['abstract'] = response.meta['abstract_']
            item['pub_time'] = time_
            item['images'] = response.meta['images_']
            yield item

