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


# author : 胡楷
class KalerkanthoSpider(BaseSpider):
    name = 'kalerkantho'
    # 下面这两个id都需要审核人修改，网站列表里没标明这俩id
    website_id = 413
    language_id = 2036
    # allowed_domains = ['']
    start_urls = ['https://www.kalerkantho.com/']


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories_1 = soup.select('div.col-xs-12 > nav.row > ul > li > a')[:6]
        categories_2 = soup.select('div.col-xs-12 > nav.row > ul > li.no-border.dropdown-online.nav-dropdown > ul > li > a')
        del categories_2[-1]
        for category in categories_1:
            category_url = category.get('href').replace('.', 'https://www.kalerkantho.com')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
        for category in categories_2:
            category_url = category.get('href').replace('.', 'https://www.kalerkantho.com')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
    # # #
    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('div.col-xs-12.mid_news > div.col-xs-12.col-sm-6.col-md-6.n_row')
        flag = True
        if OldDateUtil.time is not None:
            a1 = articles[-1].select_one('a').get('href')
            y1 = a1.split('/', 7)[3]
            m1 = a1.split('/', 7)[4]
            d1 = a1.split('/', 7)[5]
            last_time = y1 + "-" + m1 + "-" + d1 + " 00:00:00"
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = article.select_one('a').get('href')
                jug = article_url.split('/', 2)[0]
                img = article.select_one('img')
                if img == None:
                    imgs = None
                else:
                    imgs = img.get('src')
                year = article_url.split('/', 7)[3]
                mouth = article_url.split('/', 7)[4]
                day = article_url.split('/', 7)[5]
                pub_time = year + "-" + mouth + "-" + day + " 00:00:00"
                if jug == '.':
                    yield Request(url=article_url.replace('.', 'https://www.kalerkantho.com'), callback=self.parse_item, meta={'category1': response.meta['category1'], 'images': imgs, 'pub_time':pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_ = soup.select_one('div.col-xs-12.col-md-8.print_edition_left > a.btn.btn-primary')
            if next_ == None:
                next_page = soup.select_one('a[rel="next"]')
                if next_page == None:
                    pass
                else:
                    yield Request(url=next_page.get('href'), callback=self.parse_page, meta=response.meta)
            else:
                next_page = next_.get('href').replace('.', 'https://www.kalerkantho.com')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    # #
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = soup.select_one('div.col-sm-12.col-md-8.details > h2').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.some-class-name2 > p') if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item
