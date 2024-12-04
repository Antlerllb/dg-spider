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


# check:wpf pass
# author : 梁智霖
class ChiangraitimesSpider(BaseSpider):
    name = 'chiangraitimes'
    website_id = 1596
    language_id = 1866
    # allowed_domains = ['chiangraitimes.com']
    start_urls = ['https://www.chiangraitimes.com/']
    # proxy = '02'
    # 403 爆的有点多qwq，拒绝请求还是怎么滴

    def parse(self, response): # 有二级目录
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('#menu-ctn-news-1 > li')[1:-1]:
            meta = {'category1': i.select_one('a > div').text, 'category2': None}
            yield Request(url=i.select_one('a').get('href'), meta=meta, callback=self.parse_page)  # 一级目录给parse_page
            try:
                if i.select_one('ul > li > a > div').text:
                    for j in i.select('ul > li'):
                        meta['category2'] = j.select_one('a > div').text
                        yield Request(url=j.select_one('a').get('href'), meta=meta, callback=self.parse_page)
            except:
                self.logger.info('No more category2!')
                continue

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        try:
            if OldDateUtil.time is not None:
                tt = soup.select(
                    '#tdi_81 > div > div > div.td-module-meta-info > div.td-editor-date > span > span.td-post-date > time')[
                    -1].get('datetime').split('T')
                last_time = tt[0] + " " + tt[1].split('+')[0]

            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                articles = soup.select('#tdi_81 > div > div')
                for article in articles:
                    article_url = article.select_one('div.td-module-meta-info > p > a').get('href')
                    response.meta['title'] = article.select_one('div.td-module-meta-info > p > a').text.lstrip()
                    tt = soup.select(
                        '#tdi_81 > div > div > div.td-module-meta-info > div.td-editor-date > span > span.td-post-date > time')[
                        -1].get('datetime').split('T')
                    response.meta['pub_time'] = tt[0] + " " + tt[1].split('+')[0]
                    response.meta['images'] = [article.select_one('div.td-image-container > div > a > span').get('data-img-url')]
                    yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
            else:
                self.logger.info("时间截止")
            if flag:
                next_page = soup.select('div.page-nav.td-pb-padding-side > a')[-1].get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        except:
            self.logger.info('no more pages.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        try:
            item['body'] = ''.join(
                paragraph.text.lstrip() for paragraph in soup.select('div.tdb-block-inner.td-fix-index > p') + soup.select('div.tdb-block-inner.td-fix-index > h2')
                + soup.select('div.tdb-block-inner.td-fix-index > h5') if paragraph.text != '' and paragraph.text != ' ')
        except:
            item['body'] = ''
        item['abstract'] = item['body'].split('\n')[0]
        yield item