# encoding: utf-8
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

import re

# author:robot-2233  review:凌敏 pass
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
    'December': '12'}


class brookingsSpiderSpider(BaseSpider):
    name = 'brooking'
    website_id = 721
    language_id = 1866
    start_urls = ['https://www.brookings.edu/news-releases/page/1/']  # 这个网站更新有点慢，出的数据量少，甚至能出到1996的新闻（惊！
    proxy = '02'
    page = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        x = soup.find_all(class_=re.compile('archive-view report news-release'))
        for i in x:
            ssd = i.select_one(' .meta').text.split(', ')
            time_ = ssd[-1].strip('\n') + '-' + OldDateUtil.EN_1866_DATE[ssd[-2].split()[0]] + '-' + (
                str(ssd[-2].split()[1]) if len(ssd[-2].split()[1]) == 2 else '0' + str(
                    ssd[-2].split()[1])) + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                try:
                    iii = i.img.get('data-src')
                except:
                    iii = None
                meta = {'pub_time_': time_, 'images_': iii}  # 如果没有图片网站会给一个默认的图片
                yield Request(i.a.get('href'), callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            brookingsSpiderSpider.page += 1
            yield Request(brookingsSpiderSpider.start_urls[0].replace('page/1/', f'page/{brookingsSpiderSpider.page}/'),
                          callback=self.parse)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = soup.select_one(' .report-title').text
        item['category1'] = 'NEWS RELEASE'
        item['category2'] = None
        item['body'] = '\n'.join([i.text for i in soup.select(' .post-body.post-body-enhanced p')])
        item['abstract'] = soup.select(' .post-body.post-body-enhanced p')[0].text
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
