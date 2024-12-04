
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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


# author : 胡楷
# check； pys pass
class BnmSpider(BaseSpider):
    name = 'bnm'
    website_id = 420
    language_id = 2036
    # allowed_domains = ['www.bnm.gov.my']
    start_urls = ['https://www.bnm.gov.my']
    # proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('div.row.px-0.ml-sm-0.ml-md-4 > p.h3.pl-2')
        for all_year in range(1996, 2023):
            all_url = 'https://www.bnm.gov.my/press-release-' + str(all_year)
            meta = {'category1': categories[0].text}
            yield Request(url=all_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        articles = soup.select('#myTable > tr a')
        flag = True
        if OldDateUtil.time is not None:
            last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = article.get('href')
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
        item['title'] = soup.select_one('div.article-header > h1').text.strip()
        t1 = soup.select_one('div.article-header span.text-small.text-muted').text
        t2 = t1.split(' ', 2)
        if t2[1] == 'Jan': t3 = '01'
        if t2[1] == 'Feb': t3 = '02'
        if t2[1] == 'Mar': t3 = '03'
        if t2[1] == 'Apr': t3 = '04'
        if t2[1] == 'May': t3 = '05'
        if t2[1] == 'Jun': t3 = '06'
        if t2[1] == 'Jul': t3 = '07'
        if t2[1] == 'Aug': t3 = '08'
        if t2[1] == 'Sep': t3 = '09'
        if t2[1] == 'Oct': t3 = '10'
        if t2[1] == 'Nov': t3 = '11'
        if t2[1] == 'Dec': t3 = '12'
        item['pub_time'] = t2[2].replace('\n', '').replace(' ', '') + '-' + t3 + '-' + t2[0].replace(' ', '') + ' 00:00:00'
        item['images'] = None
        #网站无图片
        item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('div.article-content-cs > p') if paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item