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



# author : 梁智霖
class ThedayspringSpider(BaseSpider):
    name = 'thedayspring'
    website_id = 2098 #id未填
    language_id = 1866 #英语
    # allowed_domains = ['thedayspring']
    start_urls = ['https://www.thedayspring.com.pk/']
    # proxy = '02'
    # 有时候会报403，文章没有问题，有的文章没有图片

    def parse(self, response): # 有二级目录
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-main-menu-1 > li')[1:10]:
            meta = {'category1': i.select_one('a').text, 'category2': None}
            yield Request(url=i.select_one('a').get('href'), meta=meta, callback=self.parse_page)  # 一级目录给parse_page
            try:
                if i.select_one('ul > li > a').text:
                    for j in i.select('ul > li > a'):
                        meta['category2'] = j.text
                        yield Request(url=j.get('href'), meta=meta, callback=self.parse_page)
            except:
                self.logger.info('No more category2!')
                continue

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        try:
            if OldDateUtil.time is not None:
                tt = soup.select(
                    'div.td-pb-span8.td-main-content > div > div > div > div > div.item-details > div > span > time')[
                    -1].get('datetime').split('T')
                last_time = tt[0] + " " + tt[1].split("+")[0]

            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                articles = soup.select('div.td-pb-span8.td-main-content > div > div > div > div')
                for article in articles:
                    article_url = article.select_one('div.item-details > h3 > a').get('href')
                    tt = article.select_one(
                        'div.item-details > div > span > time').get('datetime').split('T')
                    response.meta['pub_time'] = tt[0] + " " + tt[1].split("+")[0]
                    yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
            else:
                self.logger.info("时间截止")
            if flag:
                if soup.select("div.td-pb-span8.td-main-content > div > div.page-nav.td-pb-padding-side > a")[-1].get('aria-label') == "next-page":
                    next_page = soup.select('div.td-pb-span8.td-main-content > div > div.page-nav.td-pb-padding-side > a')[-1].get('href')
                    yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        except:
            self.logger.info('no more pages.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('div.td-post-header > header > h1').text
        item['pub_time'] = response.meta['pub_time']
        try:
            if soup.select_one('div.td-post-content.tagdiv-type > div.td-post-featured-image > figure > a > img'):
                item['images'] = [img.get('src') for img in
                              soup.select('div.td-post-content.tagdiv-type > div.td-post-featured-image > figure > a > img')]
            if soup.select_one('div.td-post-content.tagdiv-type > div.td-post-featured-image > a > img'):
                item['images'] = [img.get('src') for img in
                              soup.select('div.td-post-content.tagdiv-type > div.td-post-featured-image > a > img')]
        except:
            item['images'] = ''
        try:
            item['body'] = ''.join(
                paragraph.text.lstrip() for paragraph in soup.select('div.td-post-content.tagdiv-type > p')
                if paragraph.text != '' and paragraph.text != ' ')
        except:
            item['body'] = ''
        item['abstract'] = item['body'].split('\n')[0]
        yield item