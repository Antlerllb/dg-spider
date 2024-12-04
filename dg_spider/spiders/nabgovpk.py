


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

ENGLISH_MONTH = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sept': '09',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}
# check: 凌敏 pass
# author : 李玲宝
# 我爬的是那个“乌尔都语”文档的网站，对接的同学说审核爬虫的人填id,那个id是我乱填的（不填会报错）
# 文章都没有图片、二级目录
class NabgovpkSpider(BaseSpider):
    name = 'nabgovpk'
    website_id = 2110
    language_id = 1866
    proxy = '02'
    start_urls = ['http://www.nab.gov.pk/']

    def parse(self, response):
        url = 'https://nab.gov.pk/press/press_release2.asp?curpage='
        yield scrapy.Request(url + '1', callback=self.parse_page, meta={'category1': 'press_release', 'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('table[width="573"] tr')[1:-1]
        if OldDateUtil.time is not None:
            t = block[-1].select_one('td').text.strip().split('-')
            last_time = f"{t[2]}-{OldDateUtil.EN_1866_DATE[t[1]]}-{t[0]}" + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                tt = i.select_one('td').text.strip().split('-')
                response.meta['pub_time'] = f"{tt[2]}-{OldDateUtil.EN_1866_DATE[tt[1]]}-{tt[0].zfill(2)}" + ' 00:00:00'
                yield Request('https://nab.gov.pk/press/' + i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        if soup.select_one('input[value="NEXT"]') is not None:
            response.meta['page'] += 1
            yield Request(response.meta['url'] + str(response.meta['page']), callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select('#table2 tr')[1].text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = []
        item['body'] = soup.select('#table2 tr')[2].text.strip()
        item['abstract'] = item['body'].split('.')[0]
        return item
