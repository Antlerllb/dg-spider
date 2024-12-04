
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

month = {
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

# author : 胡楷
class SangbadpratidinSpider(BaseSpider):
    name = 'sangbadpratidin'
    # 下面这两个id都需要审核人修改，网站列表里没标明这俩id
    website_id = 2261
    language_id = 1779
    # allowed_domains = ['']
    start_urls = ['https://www.sangbadpratidin.in/']


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('ul.nav.mymenu > li a')[4:26]
        for category in categories:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('ul.more_news_list.clearfix > li')
        flag = True
        if OldDateUtil.time is not None:
            tp = articles[-1].select_one('div.news_description_box > p > span').text.strip().replace(",", "").split(" ", 6)
            last_time = tp[3] + "-" + month[tp[1]] + "-" + tp[2] + " " + tp[4] + ":00"
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = article.select_one('div.more_news > a').get('href')
                t = article.select_one('div.news_description_box > p > span').text.strip().replace(",", "").split(" ", 6)
                pub_time = t[3] + "-" + month[t[1]] + "-" + t[2] + " " + t[4] + ":00"
                imgs = [img.get('src') for img in soup.select('img')]
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'pub_time': pub_time, 'images': imgs})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_ = soup.select_one('a.next_btn')
            if next_ == None:
                pass
            else:
                next_page = next_.get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
    # # #
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = soup.select_one('div.hot_news > h1').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.sp-single-post > p') if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item
