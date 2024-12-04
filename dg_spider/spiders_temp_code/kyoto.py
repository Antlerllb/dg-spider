

from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
from lxml import etree
import re

class KyotoSpider(BaseSpider):
    author = "劳宇萍"
    name = 'kyoto'
    language_id = 1963
    website_id = 804
    start_urls = ['https://kyoto.cseas.kyoto-u.ac.jp/news/']
    lan_num = 1

    @staticmethod
    def clear_category(category):
        new_category = category.replace(' ', '').replace('\n', '')
        return new_category

    @staticmethod
    def clear_body(body_list):
        new_text = ''
        japanese_kana_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]+')
        for i, text in enumerate(body_list):
            if bool(japanese_kana_pattern.search(text)):
                new_text += text.replace('\u3000', '').replace('\n      \n', '\n').replace('\n\n\n\n', '\n') + '\n'
        new_text = re.sub(r'[a-zA-Z]', '', new_text)
        return new_text

    def parse(self, response):
        page = etree.HTML(response.text)
        news_category = page.xpath('//*[@id = "news_tab_content_news"]/aside/div[1]/ul/li/a/@href')
        category = page.xpath('//*[@id = "news_tab_content_news"]/aside/div[1]/ul/li/a/text()')
        for index, new_category in enumerate(news_category):
            new_category = news_category[index]
            category1 = KyotoSpider.clear_category(category[index])
            response.meta['category1'] = category1
            yield scrapy.Request(url=new_category, callback=self.parse_category, meta=response.meta)
        events_category = page.xpath('/html/body/section/article[2]/aside/div[1]/ul/li/a/@href')
        category_ = page.xpath('/html/body/section/article[2]/aside/div[1]/ul/li/a/text()')
        for index, events_category in enumerate(events_category):
            event_category = events_category[index]
            category1 = KyotoSpider.clear_category(category_[index])
            response.meta['category1'] = category1
            yield scrapy.Request(url=event_category, callback=self.parse_category_event, meta=response.meta)

    def parse_category(self, response):
        page = etree.HTML(response.text)
        news_link = page.xpath('//*[@id="site"]/body/section/div/ul/li/a/@href')
        abstract = page.xpath('//*[@class="excerpt fs_12r sm_fs_13r lh_15e mb_1r"]/text()')
        img = page.xpath('//*[@class="image_wrap date_image_wrap fit_image_wrap"]/img/@src')
        for index, new_link in enumerate(news_link):
            response.meta['abstract'] = abstract[index]
            response.meta['img'] = img[index]
            yield scrapy.Request(url=new_link, callback=self.parse_item, meta=response.meta)
        next_page = page.xpath('/html/body/section/div/nav/a[last()]/@href')[0]
        if next_page != '#' and next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse_category, meta=response.meta)

    def parse_category_event(self, response):
        page = etree.HTML(response.text)
        news_link = page.xpath('//*[@class="hover_effect"]/@href')
        abstract1 = page.xpath('//*[@class="event_meta event_date fs_13r sm_fs_14r lh_13"]/text()')
        abstract2 = page.xpath('//*[@class="event_meta event_place fs_13r sm_fs_14r lh_13"]/text()')
        img = page.xpath('/html/body/section/article[2]/div/ul/li/a/div[1]/img/@src')
        for index, new_link in enumerate(news_link):
            response.meta['abstract'] = abstract1[index] + abstract2[index]
            response.meta['img'] = img[index]
            yield scrapy.Request(url=new_link, callback=self.parse_item, meta=response.meta)
        next_page = page.xpath('/html/body/section/div/nav/a[last()]/@href')[0]
        if next_page != '#' and next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse_category_event, meta=response.meta)


    def parse_item(self, response):
        page = etree.HTML(response.text)
        category1 = response.meta['category1']
        pub_time = page.xpath('//*[@id="site"]/body/section/header/p[2]/text()')[0] + ' 00:00:00'
        title = page.xpath('//*[@id="site"]/body/section/header/h1/span/text()')[0]
        title = re.sub(r'[a-zA-Z]', '', title)
        body_list = page.xpath('//*[@id="site"]/body/section/main//text()')
        body = KyotoSpider.clear_body(body_list)
        images = [response.meta['img']]
        if body:
            item = NewsItem(language_id=self.language_id)
            item['title'] = title
            item['pub_time'] = pub_time
            item['category1'] = category1
            item['images'] = images
            item['abstract'] = response.meta['abstract']
            item['body'] = body
            yield item




