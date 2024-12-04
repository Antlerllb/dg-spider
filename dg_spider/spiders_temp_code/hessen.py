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
class HessenSpider(BaseSpider):  # author：田宇甲
    name = 'hessen'
    website_id = 1701
    language_id = 1898
    start_urls = ['https://www.hessen.de/Medienraum?page=0']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .row .col-12 .row.mb-4 .article'):
            try:  # 有的新闻没有时间
                ssd = i.select_one(' .date.my-0').text.split('.')
                time_ = ssd[-1]+'-'+ssd[1]+'-'+ssd[0] + ' 00:00:00'
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    meta = {'pub_time_': time_, 'title_': i.h2.text.strip().strip('\n'),
                            'category1_': i.select_one(' .publisher.my-0').text.strip().strip('\n'),
                            'images_': ['https://www.hessen.de'+i.picture.img['data-src']]}
                    yield Request('https://www.hessen.de/'+i.a['href'], callback=self.parse_item, meta=meta)
            except:
                pass
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request(response.url.replace('page=' + response.url.split('page=')[1], 'page=' + str(int(response.url.split('page=')[1]) + 1)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .cp-richtext__field-richtext.cke-richtext-content.mt-3 p')])
        item['abstract'] = soup.select(' .cp-richtext__field-richtext.cke-richtext-content.mt-3 p')[0].text
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
