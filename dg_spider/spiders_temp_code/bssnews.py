
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy  
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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

li=[]
# author : 胡楷
class BssnewsSpider(BaseSpider):
    name = 'bssnews'
    website_id = 2252
    language_id = 1779
    # allowed_domains = ['']
    start_urls = ['https://www.bssnews.net/']


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories_1 = soup.select('li.nav-item.header_li.position-relative > a')[:5]
        categories_2 = soup.select('li.nav-item.header_li.position-relative > ul > li > a')[0:11]
        for category in categories_1:
            category_url = category.get('href')
            meta = {'category1': category.text, 'category2': None}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
        for category in categories_2:
            category_url = category.get('href')
            meta = {'category1': 'News', 'category2': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
    # # #
    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('div.col-lg-4.col-sm-4 > div.allnews.bg-white.pl-2.pr-2 > a')
        flag = True
        if OldDateUtil.time is not None:
            tq = articles[-1].select_one('div.post_date').text.strip().replace(',', '').split(' ', 4)
            if tq[1] == 'Jan': tq[1] = '01'
            if tq[1] == 'Feb': tq[1] = '02'
            if tq[1] == 'Mar': tq[1] = '03'
            if tq[1] == 'Apr': tq[1] = '04'
            if tq[1] == 'May': tq[1] = '05'
            if tq[1] == 'Jun': tq[1] = '06'
            if tq[1] == 'Jul': tq[1] = '07'
            if tq[1] == 'Aug': tq[1] = '08'
            if tq[1] == 'Sep': tq[1] = '09'
            if tq[1] == 'Oct': tq[1] = '10'
            if tq[1] == 'Nov': tq[1] = '11'
            if tq[1] == 'Dec': tq[1] = '12'
            last_time = tq[2] + '-' + tq[1] + '-' + tq[0] + ' ' + tq[3] + ':00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = article.get('href')
                t = article.select_one('div.post_date').text.strip().replace(',', '').split(' ', 4)
                if t[1] == 'Jan': t[1] = '01'
                if t[1] == 'Feb': t[1] = '02'
                if t[1] == 'Mar': t[1] = '03'
                if t[1] == 'Apr': t[1] = '04'
                if t[1] == 'May': t[1] = '05'
                if t[1] == 'Jun': t[1] = '06'
                if t[1] == 'Jul': t[1] = '07'
                if t[1] == 'Aug': t[1] = '08'
                if t[1] == 'Sep': t[1] = '09'
                if t[1] == 'Oct': t[1] = '10'
                if t[1] == 'Nov': t[1] = '11'
                if t[1] == 'Dec': t[1] = '12'
                pub_time = t[2] + '-' + t[1] + '-' + t[0] + ' ' + t[3] + ':00'
                if article_url == None:
                    pass
                else:
                    yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'category2': response.meta['category2'], 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_ = soup.select_one('div.col-md-12 > a.my-2.text-center')
            if next_ == None:
                next_page = soup.select_one('li.next-btn > a')
                page_jug = soup.select_one('li.next-btn.disabled > a')
                if next_page == None or page_jug != None:
                    pass
                else:
                    yield Request(url=next_page.get('href'), callback=self.parse_page, meta=response.meta)
            else:
                next_page = next_.get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
    # # #
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('div.headline_section.mb-2 > h4').text.strip()
        item['pub_time'] = response.meta['pub_time']
        imgs = soup.select_one('div.dtl_section img')
        if imgs == None:
            item['images'] = None
        else:
            item['images'] = 'https://www.bssnews.net' + imgs.get('src')
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.dtl_section > p') if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]

        yield item
