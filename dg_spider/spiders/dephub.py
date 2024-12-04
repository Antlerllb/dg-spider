


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

INDONESIA_MONTH = {
    'Januari': '01',
    'Februari': '02',
    'Pebruari': '02',
    'Maret': '03',
    'April': '04',
    'Mei': '05',
    'May': '05',
    'Juni': '06',
    'Juli': '07',
    'Agustus': '08',
    'September': '09',
    'Oktober': '10',
    'November': '11',
    'Desember': '12',
    'January': '01',
    'February': '02',
    'March': '03',
    'June': '06',
    'July': '07',
    'August': '08',
    'October': '10',
    'December': '12',
}

# author : 李玲宝
# check；凌敏 pass
class DephubSpider(BaseSpider):
    name = 'dephub'
    website_id = 82
    language_id = 1866
    start_urls = ['http://dephub.go.id/post/kategori?category=berita&page=1']

    def parse(self, response):
        url = 'http://dephub.go.id/post/kategori?category=berita&page=1'
        yield scrapy.Request(url, callback=self.parse_page, meta={'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if (soup.select_one('#category-post .col') is None):  # 没有文章了，爬虫结束，退出函数
            self.logger.info("时间截止")
            return 1
        block = soup.select('#category-post .col')
        flag = True
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.media-date-small').string.strip().split(' ')
            last_time = f'{t[3]}-{INDONESIA_MONTH[t[2]]}-{t[1]}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                url = 'http://dephub.go.id' + i.select_one('a')['href']
                tt = i.select_one('.media-date-small').string.strip().split(' ')
                response.meta['pub_time'] = f'{tt[3]}-{INDONESIA_MONTH[tt[2]]}-{tt[1]}' + ' 00:00:00'
                response.meta['category1'] = soup.select_one('div.content-title').text.strip()
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            response.meta['page'] += 1
            url = response.meta['url'].split('&page=')[0] + '&page=' + str(response.meta['page'])  # 页码+1后的url
            yield Request(url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h4').text
        item['abstract'] = soup.select_one('div.media-description>p').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = ['http:' + img.get('src') for img in soup.select('div.media-description img')]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('div.media-description>p'))
        return item
