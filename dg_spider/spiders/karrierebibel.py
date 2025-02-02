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

# check:魏芃枫 pass

class KarrierebibelSpider(BaseSpider):  # author：田宇甲
    name = 'karrierebibel'
    website_id = 1776
    language_id = 1898
    start_urls = [f'https://karrierebibel.de/tipps/{i}/' for i in ['finanzen', 'management', 'berufsbild', 'knigge', 'selbststaendig', 'studium-ausbildung', 'lesenswert', 'job-psychologie', 'bewerbung']]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .row.blog__row .col-md-6.col-lg-4'):
            meta = {'title_': i.select_one(' .article__content').text.strip(), 'category1_': response.url.split('tipps/')[1].split('/')[0]}
            yield Request(i.a['href'], callback=self.check_check, meta=meta)
        if 'page' not in response.url:
            yield Request(response.url+'page/1/')
        else:
            yield Request(response.url.split('page/')[0]+'page/'+str(int(response.url.split('page/')[1].strip('/'))+1)+'/')

    def check_check(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        ssd = soup.select_one(' .post__date').text.split(': ')[1].split('.')
        time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.meta['title_']
            item['category1'] = response.meta['category1_']
            item['category2'] = None
            item['body'] = soup.select_one(' .entry-content').text.strip().strip('\n')
            item['abstract'] = soup.select_one(' .post__intro').text.strip().strip('\n')
            item['pub_time'] = time_
            item['images'] = [soup.select_one(' .post__featured img')['data-src']]
            yield item

