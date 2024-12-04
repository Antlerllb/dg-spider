


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


# author : 沈振兴

class A7jpzSpider(BaseSpider):
    name = '7jpz'
    allowed_domains = ['7jpz.com']
    website_id = 1881
    language_id = 2266
    start_urls = ['https://www.7jpz.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('#xlmm-leftnav>ul>li>a')[1]
        category_url = soup.select('#xlmm-leftnav>ul>li>a')[1].get('href')
        meta = {'category1': categories.text}
        yield Request(url=category_url, callback=self.parse_col, meta=meta)

    def parse_col(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        columns = soup.select('div.subchannel > ul > li a')[1:]
        for i in columns:
            response.meta['category2'] = i.text
            column_url = i.get('href')
            yield Request(url=column_url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        test = soup.select('div > span.subinfo.S_txt2')
        if len(test) != 0:
            t_ori = test[-1].text
        else:
            t_ori = soup.select('#alist > li > div > div > div.grxx.mt10 > a.hfsj.h20')[-1].text
        t_ori += ':00'
        t = t_ori
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(t) >= int(OldDateUtil.time):
            articles = soup.select('#alist > li > div > div div.div1twz > a')
            response.meta['pub_time'] = t
            for article in articles:
                article_url = article.get('href')
                yield Request(url=article_url, callback=self.parse_item, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        response.meta['title'] = soup.select_one('div > div > h1').text
        images = [i.get('src') for i in soup.select('div.bm.vw p img')]
        images = [('https://www.7jpz.com/' + i) if i[:4] != 'http' else i for i in images]
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        if len(soup.select('#article_content div')) != 0:
            item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('#article_content div') if
                                      paragraph.text != '' and paragraph.text != ' '])
        elif len(soup.select('#article_content>p')) != 0:
            item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('#article_content>p') if
                                      paragraph.text != '' and paragraph.text != ' '])
        else:
            item['body'] = '\n'.join([paragraph.text.strip() for paragraph in soup.select('#article_content>p span') if
                                      paragraph.text != '' and paragraph.text != ' '])
        test = soup.select_one('div.quotation p')
        if len(test) != 0:
            item['abstract'] = test.text
        else:
            item['abstract'] = item['body'].split('\n')[0]
        item['pub_time'] = response.meta['pub_time']
        item['images'] = images
        yield item
