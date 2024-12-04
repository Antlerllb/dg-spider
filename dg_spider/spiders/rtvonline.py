


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
    'Dec': '12',
    'JANUARY': '01',
    'FEBRUARY': '02',
    'MARCH': '03',
    'APRIL': '04',
    'MAY': '05',
    'JUNE': '06',
    'JULY': '07',
    'AUGUST': '08',
    'SEPTEMBER': '09',
    'OCTOBER': '10',
    'NOVEMBER': '11',
    'DECEMBER': '12',
}

# author : 李玲宝
# check: 凌敏 pass
class RtvonlineSpider(BaseSpider):
    name = 'rtvonline'
    website_id = 1918
    language_id = 1866
    proxy = '02'
    start_urls = ['https://www.rtvonline.com/english/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.select('#menu_category>ul>li')[:-1]
        for i in menu:
            for j in i.select('li'):
                old_url_arr = j.select_one('a')['href'].split('english/')
                new_url = 'https://www.rtvonline.com/english/all-news/' + old_url_arr[1] + '/?pg=1'
                yield scrapy.Request(new_url, callback=self.parse_page, meta={'category1': i.select_one('a').text, 'category2': j.select_one('a').text, 'url': new_url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if (soup.select_one('div.all_news_content_block .col-md-6') is None):  # 没有文章了，爬虫结束，退出函数
            self.logger.info("时间截止")
            return 1
        block = soup.select('div.all_news_content_block .col-md-6')  # 每个新闻块
        max_page = soup.select_one('li.disabled').text.strip().split('of ')[1]  # 网站没有self.time，翻页要用
        if response.meta['page'] <= int(max_page):
            for i in block:
                tt = i.select_one('.post_date').text.split(', ')[0].split(' ')
                response.meta['pub_time'] = f'{tt[2]}-{OldDateUtil.EN_1866_DATE[tt[1]]}-{tt[0]}' + ' 00:00:00'
                yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        if response.meta['page'] < int(max_page):
            response.meta['page'] += 1
            url = response.meta['url'].split('/?pg=')[0] + '/?pg=' + str(response.meta['page'])  # 页码+1后的url
            yield Request(url, callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('div.headline_section').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('div.dtl_section div.img img')]
        body_arr = soup.select_one('div.dtl_section').text.split('\n')
        item['body'] = '\n'.join(i.strip() for i in body_arr if (i != '' and i != '\xa0' and i !='Photo: Collected'))
        item['abstract'] = item['body'].split('\n')[0]
        return item
