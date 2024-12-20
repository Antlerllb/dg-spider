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
class InquirernetSpider(BaseSpider):
    name = 'inquirernet'
    website_id = 845
    language_id = 1866
    # allowed_domains = ['www.inquirer.net']
    start_urls = ['https://www.inquirer.net/']  # https://www.inquirer.net/
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        categories = soup.select('#main_nav > ul > li > a')
        del categories[3]
        for category in categories:
            yield Request(url='https:' + category.get('href'), callback=self.parse_cate2, meta={'category1': category.text})

    def parse_cate2(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.select('#subchannels > ul > li > a'):
            if i.get('href') == '//cebudailynews.inquirer.net/':
                continue
            if i.get('href') == '//newsinfo.inquirer.net/regions':
                yield Request(url='https:' + i.get('href'), callback=self.parse_cate3, meta={'category1': response.meta['category1'], 'category2': i.text})
            else:
                yield Request(url='https:' + i.get('href'), callback=self.parse_page, meta={'category1': response.meta['category1'], 'category2': i.text})

    def parse_cate3(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.select('#channel-lbl > a'):
            yield Request(url='https:' + i.get('href'), callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('#ch-ls-head')
        if OldDateUtil.time is not None:
            t = articles[-1].select_one('#ch-postdate').text.replace(',', ' ').split(' ')
            last_time = "{}-{}-{}".format(t[3], str(OldDateUtil.EN_1866_DATE[t[0]]).zfill(2), t[1]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.select_one('#ch-postdate').text.replace(',', ' ').split(' ')
                pub_time = "{}-{}-{}".format(tt[3], str(OldDateUtil.EN_1866_DATE[tt[0]]).zfill(2), tt[1]) + ' 00:00:00'
                article_url = article.select_one('h2 > a').get('href')
                title = article.select_one('h2 > a').text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'], 'category2': response.meta['category2'], 'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = soup.select('#ch-more-news a')[-1].get('href')
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('#article_level_wrap #article_content img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('#article_level_wrap #article_content p') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item

