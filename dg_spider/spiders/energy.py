# encoding: utf-8



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


#   Author:叶雨婷
Tai_MONTH = {
        'มกราคม': '01',
        'กุมภาพันธ์': '02',
        'มีนาคม': '03',
        'เมษายน': '04',
        'พฤษภาคม': '05',
        'มิถุนายน': '06',
        'กรกฎาคม': '07',
        'สิงหาคม': '08',
        'กันยายน': '09',
        'ตุลาคม': '10',
        'พฤศจิกายน': '11',
        'ธันวาคม': '12'}

class EnergySpider(BaseSpider):
    name = 'energy'
    start_urls = ['https://old.energy.go.th/']
    website_id = 1614
    language_id = 2208

    # 拿几个含新闻内容的模块的html文件的，改名字了好像，原来的也no page了
    def parse(self, response):
        list_pages = ["category/minister-news-th/", "category/executive-news-th/"]
        for item in list_pages:
            meta_part = {'e': item}
        yield Request(url=self.start_urls[0] + item, callback=self.get_page, meta=meta_part)

    # 由于分类一次后每篇文章没有显示时间，所以这个parse没有时间判断
    def get_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('h2[class="entry-title"] a'):
            yield Request(url=i.get('href'), callback=self.parse_time)
        try:
            yield Request(url=soup.select_one(' .next.page-numbers').get('href'))
            # 翻页
        except AttributeError:
            pass

    # 每一篇文章都进行一次parse_time，顺便item
    def parse_time(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        t = soup.select_one('time').text.split(',')[1].split(' ')
        last_time = str(t[3]) + "-" + Tai_MONTH[t[2]] + "-" + str(t[1]) + " 00:00:00"
        item = NewsItem(language_id=self.language_id)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            item['title'] = soup.select_one('header[class="entry-header"]').text
            item['pub_time'] = last_time
            item['images'] = soup.select_one('img').get('src')
            try:
                item['body'] = soup.select_one(' .entry-content p').text
            except AttributeError:
                item['body'] = 'None'
            item['category1'] = "หน้าแรก"
            item['abstract'] = " "
            item['category2'] = "ข่าวสารรัฐมนตรี"
            yield item