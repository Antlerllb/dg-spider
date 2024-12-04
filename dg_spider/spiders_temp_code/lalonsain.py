


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
import re

# encoding: utf-8

# 英语月份对照表
BENGALI_MONTH = {
    'জানুয়ারী': '01',
    'জানুয়ারি': '01',
    'ফেব্রুয়ারী': '02',
    'ফেব্রুয়ারি': '02',
    'মার্চ': '03',
    'এপ্রিল': '04',
    'মে': '05',
    'জুন': '06',
    'জুলাই': '07',
    'আগস্ট': '08',
    'অগাষ্ট': '08',
    'সেপ্টেম্বর': '09',
    'অক্টোবর': '10',
    'নভেম্বর': '11',
    'ডিসেম্বর': '12',
}

# author : 李玲宝
# 文章都没有图片
# check: 凌敏 pass
class LalonsainSpider(BaseSpider):
    name = 'lalonsain'
    website_id = 1906
    language_id = 1779
    start_urls = ['https://lalonsain.wordpress.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#categories-2>ul>li>a'):
            url = i['href'] + 'page/'
            yield scrapy.Request(url + '1/', callback=self.parse_item, meta={'category1': i.text.strip(), 'page': 1})

    def parse_item(self, response):  # 因为新闻列表页面就已经有所有正文了，所以在这里就爬文章内容
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.select_one('#content-body>div a') is None:  # 没有文章了，爬虫结束，退出函数
            self.logger.info("时间截止")
            return 1
        block = soup.select('#content-body>div')[:-1]
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.post-date').text.strip().split(' ')
            last_time = f'{t[-1]}-{BENGALI_MONTH[t[0]]}-{t[1][:-1]}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                item = NewsItem(language_id=self.language_id)
                item['category1'] = response.meta['category1']
                item['title'] = soup.select_one('.post-date>a')['title']
                tt = soup.select_one('.post-date').text.strip().split(' ')
                item['pub_time'] = f'{tt[-1]}-{BENGALI_MONTH[tt[0]]}-{tt[1][:-1]}' + ' 00:00:00'
                item['images'] = []
                item['body'] = '\n'.join(i.text.strip() for i in soup.select('.entry>p') if i.text.strip() != '')
                item['abstract'] = item['body'].split('\n')[0]
                return item
