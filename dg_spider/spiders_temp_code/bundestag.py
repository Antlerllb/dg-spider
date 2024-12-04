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
# check: wpf pass
class BundestagSpider(BaseSpider):  # author：田宇甲
    name = 'bundestag'
    website_id = 1692
    language_id = 1898
    start_urls = ['https://www.bundestag.de/ajax/filterlist/de/presse/pressemitteilungen/454504-454504?limit=20&noFilterSet=true&offset=0']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .bt-listenteaser ul li'):
            meta = {'title_': i.a.text.strip(), 'category1_': 'pressemitteilungen'}
            yield Request('https://www.bundestag.de'+i.a['href'], callback=self.check_check, meta=meta)
        yield Request(response.url.split('&offset=')[0]+'&offset='+str(int(response.url.split('&offset=')[1])+1))

    def check_check(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        ssd = soup.select_one(' .bt-date').text.strip().split(' ')
        time_ = ssd[-1] + '-' + German_month[ssd[1]] + '-' + ssd[0].strip('.') + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.meta['title_']
            item['category1'] = response.meta['category1_']
            item['category2'] = None
            item['body'] = ''.join([i.text for i in soup.select(' .row article p')[1:]])
            item['abstract'] = soup.select(' .row article p')[1].text.strip().strip('\n')
            item['pub_time'] = time_
            item['images'] = []
            yield item

