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



# author : 武洪艳
class OurdailynewsonlinecomSpider(BaseSpider):
    name = 'ourdailynewsonlinecom'
    website_id = 1175
    language_id = 1866
    # allowed_domains = ['ourdailynewsonline.com/']
    start_urls = ['https://ourdailynewsonline.com/']  # https://ourdailynewsonline.com/

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for category in soup.select('.main-navigation #menu-daily-news > li')[2:7]:
            category1 = category.select_one('li > a').text
            for i in category.select('.sub-menu > li > a'):
                yield Request(url=i.get('href'), callback=self.parse_page, meta={'category1': category1, 'category2': i.text})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.row .card_content')
        if OldDateUtil.time is not None:
            t = articles[-1].select_one('.posted_date .entry-date.published').text.replace(',', ' ').split(' ')
            last_time = "{}-{}-{}".format(t[3], str(OldDateUtil.EN_1866_DATE[t[0]]).zfill(2), t[1]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.select_one('.posted_date .entry-date.published').text.replace(',', ' ').split(' ')
                pub_time = "{}-{}-{}".format(tt[3], str(OldDateUtil.EN_1866_DATE[tt[0]]).zfill(2), tt[1]) + ' 00:00:00'
                article_url = article.select_one('.post_title a').get('href')
                title = article.select_one('.post_title a').text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'category2': response.meta['category2'], 'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('div.pagination .nav-links a.next.page-numbers') == None:
                self.logger.info("no more pages")
            else:
                next_page = soup.select_one('div.pagination .nav-links a.next.page-numbers').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.content-entry > article > div.the_content img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('.content-entry > article > div.the_content p') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        return item
