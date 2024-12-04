


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

URDU_MONTH = {
    'جنوری': '01',
    'فبروری': '02',
    'مارچ': '03',
    'اپریل': '04',
    'مئی': '05',
    'جون': '06',
    'جولائی': '07',
    'جولای': '07',
    'اگوسٹ': '08',
    'سپٹمبر': '09',
    'ستمبر': '09',
    'اکتوبر': '10',
    'نومبر': '11',
    'دسمبر': '12'
}

# author : 李玲宝
# check: 凌敏 pass
# 我爬的是那个“乌尔都语”文档的网站，对接的同学说审核爬虫的人填id,那个id是我乱填的（不填会报错）
class GooglynewsSpider(BaseSpider):
    name = 'googlynews'
    website_id = 2091
    language_id = 2238
    start_urls = ['https://googlynews.tv']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('#menu-main a')
        for i in category1[2:11] + category1[12:-1]:
            url = i['href'] + 'page/'
            yield scrapy.Request(url + '1/', callback=self.parse_page, meta={'category1': i.text.strip(), 'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('#posts-container li')
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.date').text.strip().split(' ')
            last_time = f"{t[2]}-{URDU_MONTH[t[1].strip(',')]}-{t[0].zfill(2)}" + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                tt = i.select_one('.date').text.strip().split(' ')
                response.meta['pub_time'] = f"{tt[2]}-{URDU_MONTH[tt[1].strip(',')]}-{tt[0].zfill(2)}" + ' 00:00:00'
                yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        if soup.select_one('.last-page') is not None:
            response.meta['page'] += 1
            yield Request(response.meta['url'] + str(response.meta['page']) + '/', callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('article img')]
        item['body'] = '\n'.join(i.strip() for i in soup.select_one('.entry-content').text.split('\n') if i.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
