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

# author:胡楷
class MetiSpider(BaseSpider):
    name = 'meti'
    website_id = 2014
    language_id = 1963
    allowed_domains = ['www.meti.go.jp']
    start_urls = ['https://www.meti.go.jp/press/index.html']
    # proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories_1 = soup.select('ul.clearfix.category_box > li > a')
        for category_1 in categories_1:
            category_1_url = 'https://www.meti.go.jp/press/' + category_1.get('href')
            meta = {'category1': category_1.text}
            yield Request(url=category_1_url, callback=self.parse_1_page, meta=meta)

    def parse_1_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('dl.date_sp.b-solid > dd > a')
        flag = True
        if OldDateUtil.time is not None:
            last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = 'https://www.meti.go.jp' + article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            pass

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('div.w1000 > #MainContentsArea').text.strip()
        tt = soup.select_one('div.main.w1000 > div.clearfix.float_box > div.left > p').text.strip()
        time = tt.replace('年', '-').replace('月', '-').replace('日', '')
        item['pub_time'] = time + ' ' + '00:00:00'
        item['images'] = None
        body = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.main.w1000') if paragraph.text != '' and paragraph.text != ' '])
        item['body'] = body.split('\n', 1)[1].replace('\n', '')
        item['abstract'] = item['body'].split('\n')[0]
        yield item