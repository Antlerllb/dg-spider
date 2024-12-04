
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
class DbklSpider(BaseSpider):
    name = 'dbkl'
    website_id = 413
    language_id = 2036
    # allowed_domains = ['']
    start_urls = ['https://www.dbkl.gov.my/']


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#jet-menu-item-6500 a.sub-level-link')[1:3]
        for category in categories:
            category_url = category.get('href')
            meta = {'category1': category.text}
            yield Request(url=category_url, callback=self.parse_page, meta=meta)
    # #
    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('div.posts-list.posts-list--default.list-style-v2 > article > header')
        flag = True
        if OldDateUtil.time is not None:
            last_time = articles[-1].select_one('div.entry-meta > span > time').get('datetime').replace('T',' ').replace('+08:00','')
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = article.select_one('h3.entry-title > a').get('href')
                pub_time = article.select_one('div.entry-meta > span > time').get('datetime').replace('T',' ').replace('+08:00','')
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_ = soup.select_one('div.nav-links > div.nav-previous > a')
            if next_ == None:
                pass
            else:
                next_page = next_.get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
    # #
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = soup.select_one('h1.entry-title.h2-style').text.strip()
        item['pub_time'] = response.meta['pub_time']
        imgs = [img.get('src') for img in soup.select('div.elementor-image > img')]
        if imgs == None:
            item['images'] = None
        else:
            item['images'] = imgs
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.elementor-text-editor.elementor-clearfix') if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]

        yield item
