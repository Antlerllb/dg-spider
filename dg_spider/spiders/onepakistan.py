


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

# author : 李玲宝
# check: 凌敏 pass 此网站语言为英语
# 我爬的是那个“乌尔都语”文档的网站，对接的同学说审核爬虫的人填id,那个id是我乱填的（不填会报错）
# 新闻量小（20左右），网站本来就没有二级标题
class OnepakistanSpider(BaseSpider):
    name = 'onepakistan'
    website_id = 2093
    language_id = 1866
    start_urls = ['http://www.onepakistan.com.pk']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('#menu-header-1>li>a')
        for i in category1[1:-2]:
            url = i['href'] + 'page/'
            yield scrapy.Request(url + '1/', callback=self.parse_page, meta={'category1': i.text.strip(), 'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('.articles article')
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.published_time').text.strip().split(' ')
            last_time = f'{t[-1]}-{OldDateUtil.EN_1866_DATE[t[0]]}-{t[1][:-1].zfill(2)}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                response.meta['pub_time'] = i.select_one('time')['datetime'] + ' 00:00:00'
                yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        if soup.select_one('.epcl-pagination a') is not None:
            response.meta['page'] += 1
            yield Request(response.meta['url'] + str(response.meta['page'] + '/'), callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.main-article img')]
        item['body'] = '\n'.join(i.strip() for i in soup.select_one('div.text').text.split('\n') if i.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
