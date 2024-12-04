


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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

ENGLISH_MONTH = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

# author : 李玲宝
# check: 凌敏 pass
class KaliokalamSpider(BaseSpider):
    name = 'kaliokalam'
    website_id = 1891
    language_id = 1779
    start_urls = ['https://www.kaliokalam.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-item-8705>ul>li'):
            for j in i.select('.depth1>li'):  # 存放二级标题
                url = j.select_one('a')['href'] + 'page/'
                yield scrapy.Request(url + '1/', callback=self.parse_page, meta={'category1': i.select_one('a')['title'], 'category2': j.select_one('a')['title'], 'page': 1, 'url': url})
            if (i.select_one('.depth1>li')) is None:  # 如果没有二级标题，i.select('.depth1>li')为空
                url = i.select_one('a')['href'] + 'page/'
                yield scrapy.Request(url + '1/', callback=self.parse_page, meta={'category1': i.select_one('a')['title'],'category2': None, 'page': 1, 'url': url})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('main.order-lg-last article')
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.meta-content').text.strip().split(' ')
            last_time = time.strftime('%Y-%m-%d', time.strptime(f"{t[2]}.{OldDateUtil.EN_1866_DATE[t[0]]}.{t[1][:-1]}", '%Y.%m.%d')) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                tt = i.select_one('.meta-content').text.strip().split(' ')
                response.meta['pub_time'] = time.strftime('%Y-%m-%d', time.strptime(f"{tt[2]}.{OldDateUtil.EN_1866_DATE[tt[0]]}.{tt[1][:-1]}", '%Y.%m.%d')) + ' 00:00:00'
                yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        if soup.select_one('div.navigation .next') is not None:
            response.meta['page'] += 1
            yield Request(response.meta['url'] + str(response.meta['page']) + '/', callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('h1.entry-title').text.strip()
        for i in soup.select('.entry-content>p'):
            if (i.text.strip() != ''):
                item['abstract'] = i.text.strip()
                break
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.entry-wrapper img')]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('.entry-content>p') if (i.text.strip() != ''))
        return item
