


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

#author: 蔡卓妍
#网站更新慢 新闻少
class BknSpider(BaseSpider):
    name = 'bkn'
    website_id = 124
    language_id = 1952
    start_urls = ['https://www.bkn.go.id/category/publikasi/berita/',
                  'https://www.bkn.go.id/category/publikasi/pengumuman/',
                  'https://www.bkn.go.id/category/publikasi/blog-kepegawaian/',
                  'https://www.bkn.go.id/category/publikasi/siaran-pers/']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        ltime = soup.select('article')[-1].select_one('.meta-date .updated').text.split('/')
        last_time = ltime[2] + '-' + ltime[1] + '-' + ltime[0] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
            category1 = soup.select_one('.page-header-content > h1').text.strip()
            lists = soup.select('article')
            for i in lists:
                title = i.select_one('header > h2 > a').text
                news_url = i.select_one('header > h2 > a').get('href')
                ptime = i.select_one('.meta-date .updated').text.split('/')
                pub_time = ptime[2] + '-' + ptime[1] + '-' + ptime[0] + ' 00:00:00'
                meta = {'title':title, 'pub_time':pub_time, 'category1':category1}
                yield Request(url=news_url,callback=self.parse_item,meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            try:
                next_page = soup.select_one('.next.page-numbers')['href']
                yield Request(url=next_page, callback=self.parse)
            except:
                self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('p'))
        if soup.select_one('p').text.strip() == '':
            item['abstract'] = soup.select('p')[1].text.strip()
        else:
            item['abstract'] = soup.select_one('p').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [i['src'] for i in (soup.select_one('article >div').select('img')+soup.find(itemprop='text').select('img'))]
        yield item