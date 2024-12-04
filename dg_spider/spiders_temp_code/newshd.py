


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
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
}

# author : 李玲宝
# check: 凌敏 pass 此网站语言为英语
# 我爬的是那个“乌尔都语”文档的网站，对接的同学说审核爬虫的人填id,那个id是我乱填的（不填会报错）
# 网站本来就没有二级标题
class NewshdSpider(BaseSpider):
    name = 'newshd'
    website_id = 2092
    language_id = 1866
    start_urls = ['https://92newshd.tv/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('#top_menu a')
        for i in category1:
            url = 'https://92newshd.tv' + i['href'] + '?pno='
            yield scrapy.Request(url + '1', callback=self.parse_page, meta={'category1': i.text.strip(), 'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('#posts .post_link')
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.published_time').text.strip().split(' ')
            last_time = f'{t[-1]}-{OldDateUtil.EN_1866_DATE[t[0]]}-{t[1][:-1].zfill(2)}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                tt = soup.select_one('.published_time').text.strip().split(' ')
                response.meta['pub_time'] = f'{tt[-1]}-{OldDateUtil.EN_1866_DATE[tt[0]]}-{tt[1][:-1].zfill(2)}' + ' 00:00:00'
                yield Request('https://92newshd.tv' + i['href'], callback=self.parse_item, meta=response.meta)
        if soup.select('a.see-more')[1].text.strip() == 'Older':
            response.meta['page'] += 1
            url = response.meta['url'] + str(response.meta['page'])  # 页码+1后的url
            yield Request(url, callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('article img')]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('.content_detail p') if i.text.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
