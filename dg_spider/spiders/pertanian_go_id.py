# encoding: utf-8
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



# author: 梁智霖

class PertaniangoidSpider(BaseSpider):
    name = 'pertanian_go_id'
    website_id = 96
    language_id = 1952
    start_urls = ["https://pertanian.go.id/home/?show=news&act=view_all&page=1"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        category1 = soup.select_one("legend > h2")
        yield Request(url=response.url,callback=self.parse_page,meta={'category1': category1.text})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('div.media')
        for article in articles:
            article_url = 'https://www.pertanian.go.id/home/' + article.select_one("div>h4>a").get('href')
            response.meta['images'] = [article.select_one('div>a>img').get('src')]
            response.meta['title'] = article.select_one('#media-heading').text
            yield Request(url=article_url,meta=response.meta,callback=self.parse_item)

        next_page = 'https://www.pertanian.go.id/home/' + soup.select_one('nav > ul > li:nth-child(8) > a').get('href')
        yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None

        #body可能有五种格式(四种新闻和一种公告)//相互独立
        body = ''
        if soup.select('div.entry-content.notopmargin > div'):
            for i in soup.select('div.entry-content.notopmargin > div'):
                body += i.text.strip()
        if soup.select('div.entry-content.notopmargin > p > span'):
            for i in soup.select('div.entry-content.notopmargin > p > span'):
                body += i.text.strip()
        if soup.select('div.entry-content.notopmargin > p'):
            for i in soup.select('div.entry-content.notopmargin > p'):
                body += i.text.strip()
        if soup.select('p.style2'):
            for i in soup.select('p.style2'):
                body += i.text.strip()
        if soup.select('span > span'):
            for i in soup.select('span > span'):
                body += i.text.strip()
        item['body'] = body

        try:
            abstract = item['body'].split('\n')[0]
            item['abstract'] = abstract
        except:
            item['abstract'] = ''

        item['images'] = response.meta['images']
        #该网站新闻无发布时间
        item['pub_time'] = OldDateUtil.get_now_datetime_str()
        yield item