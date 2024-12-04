# -*- coding: utf-8 -*-
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil





from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

class VodkhmerSpider(BaseSpider):
    author = '王伟任'
    name = 'vodkhmer'
    website_id = 2686
    language_id = 2275
    start_urls = ['https://www.vodkhmer.news/category/national/']
    lan_num = 1
    def parse(self, response):

        for num in range(1,11):
            date_news = response.xpath(
                f'//div[@class="elementor-widget-container"]/div/article[{num}]/div/div[@ class="elementor-post__meta-data"]/span[@class="elementor-post-date"]/text()').extract_first()
            time_news = response.xpath(
                f'//div[@class="elementor-widget-container"]/div/article[{num}]/div/div[@ class="elementor-post__meta-data"]/span[@class="elementor-post-time"]/text()').extract_first()

            date_news_cut = date_news.split(" ")

            date_news_cut[3] = str(date_news_cut[3]).replace("០", "0")
            date_news_cut[3] = str(date_news_cut[3]).replace("១", "1")
            date_news_cut[3] = str(date_news_cut[3]).replace("២", "2")
            date_news_cut[3] = str(date_news_cut[3]).replace("៣", "3")
            date_news_cut[3] = str(date_news_cut[3]).replace("៤", "4")
            date_news_cut[3] = str(date_news_cut[3]).replace("៥", "5")
            date_news_cut[3] = str(date_news_cut[3]).replace("៦", "6")
            date_news_cut[3] = str(date_news_cut[3]).replace("៧", "7")
            date_news_cut[3] = str(date_news_cut[3]).replace("៨", "8")
            date_news_cut[3] = str(date_news_cut[3]).replace("៩", "9")
            year_time = date_news_cut[3]
            if date_news_cut[2] == 'មករា':
                date_news_cut[2] = '01'
            elif date_news_cut[2] == 'កុម្ភៈ':
                date_news_cut[2] = '02'
            elif date_news_cut[2] == 'មីនា':
                date_news_cut[2] = '03'
            elif date_news_cut[2] == 'មេសា':
                date_news_cut[2] = '04'
            elif date_news_cut[2] == 'ឧសភា':
                date_news_cut[2] = '05'
            elif date_news_cut[2] == 'មិថុនា':
                date_news_cut[2] = '06'
            elif date_news_cut[2] == 'កក្កដា':
                date_news_cut[2] = '07'
            elif date_news_cut[2] == 'សីហា':
                date_news_cut[2] = '08'
            elif date_news_cut[2] == 'កញ្ញា':
                date_news_cut[2] = '09'
            elif date_news_cut[2] == 'តុលា':
                date_news_cut[2] = '10'
            elif date_news_cut[2] == 'វិច្ឆិកា':
                date_news_cut[2] = '11'
            elif date_news_cut[2] == 'ធ្នូ':
                date_news_cut[2] = '12'
            month_time = date_news_cut[2]
            if len(date_news_cut[1]) == 1:
                date_news_cut[1] = "0" + date_news_cut[1]
            date_news_cut[1] = str(date_news_cut[1]).replace("០", "0")
            date_news_cut[1] = str(date_news_cut[1]).replace("១", "1")
            date_news_cut[1] = str(date_news_cut[1]).replace("២", "2")
            date_news_cut[1] = str(date_news_cut[1]).replace("៣", "3")
            date_news_cut[1] = str(date_news_cut[1]).replace("៤", "4")
            date_news_cut[1] = str(date_news_cut[1]).replace("៥", "5")
            date_news_cut[1] = str(date_news_cut[1]).replace("៦", "6")
            date_news_cut[1] = str(date_news_cut[1]).replace("៧", "7")
            date_news_cut[1] = str(date_news_cut[1]).replace("៨", "8")
            date_news_cut[1] = str(date_news_cut[1]).replace("៩", "9")
            date_time = date_news_cut[1]

            time_news_cut = time_news.split(" ")
            time_news_cut_cut = time_news_cut[1].split(":")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("០", "0")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("១", "1")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("២", "2")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("៣", "3")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("៤", "4")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("៥", "5")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("៦", "6")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("៧", "7")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("៨", "8")
            time_news_cut_cut[0] = str(time_news_cut_cut[0]).replace("៩", "9")

            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("០", "0")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("១", "1")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("២", "2")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("៣", "3")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("៤", "4")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("៥", "5")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("៦", "6")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("៧", "7")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("៨", "8")
            time_news_cut_cut[1] = str(time_news_cut_cut[1]).replace("៩", "9")
            hour_time = time_news_cut_cut[0]
            min_time = time_news_cut_cut[1]
            pub_time = f"{year_time}-{month_time}-{date_time} {hour_time}:{min_time}:00"
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            images = response.xpath(f'//div [@class="elementor-widget-container"]/div/article[{num}]/div/a/@href').extract()

            title = response.xpath(f'//div [@class="elementor-widget-container"]/div/article[{num}]/div/div/h2/a/text()').extract_first()
            title = "".join(title)
            title = title.replace("\u200b", "")
            title =  title.replace("\xa0", "")
            title =  title.replace("\n", "")

            abstract = response.xpath(f'//div[@class="elementor-widget-container"]/div/article[{num}]/div/div/div[@class="elementor-post__excerpt"]/p/text()').extract_first()
            abstract = "".join(abstract)
            abstract = abstract.replace("\u200b", "")
            abstract =  abstract.replace("\xa0", "")
            abstract =  abstract.replace("\n", "")

            class_url = response.xpath(f'//div [@class="elementor-widget-container"]/div/article[{num}]/div/div/h2/a/@href').extract_first()
            response.meta['title'] = title
            response.meta['abstract'] = abstract
            response.meta['images'] = images
            response.meta['pub_time'] = pub_time
            yield scrapy.Request(class_url,callback=self.parse_item, meta=response.meta)
        for num_first in range(2,50):
            new_first_url = f'https://www.vodkhmer.news/category/national/page/{num_first}/'
            category1 = "អន្តរជាតិ"
            response.meta['class_url'] = new_first_url
            response.meta['category1'] = category1
            yield scrapy.Request(new_first_url, callback=self.parse, meta=response.meta)
        for num_secord in range(1,50):
            new_secord_url = f'https://www.vodkhmer.news/category/international-news/page/{num_secord}/'
            category1 = "ព័ត៌មានជាតិ"
            response.meta['class_url'] = new_secord_url
            response.meta['category1'] = category1
            yield scrapy.Request(new_secord_url, callback=self.parse, meta=response.meta)
        for num_third in range(1,50):
            new_third_url = f'https://www.vodkhmer.news/category/international-news/page/{num_third}/'
            category1 = "បោះឆ្នោត"
            response.meta['class_url'] = new_third_url
            response.meta['category1'] = category1
            yield scrapy.Request(new_third_url, callback=self.parse, meta=response.meta)
        for num_forth in range(1,50):
            new_forth_url = f'https://www.vodkhmer.news/category/national/political-issues/politics/page/{num_forth}/'
            category1 = "បញ្ហានយោបាយ"
            response.meta['class_url'] = new_forth_url
            response.meta['category1'] = category1
            yield scrapy.Request(new_forth_url, callback=self.parse, meta=response.meta)
        for num_ninth in range(1,49):
            new_ninth_url = f'https://www.vodkhmer.news/category/national/political-issues/court-and-law/page/{num_ninth}/'
            category1 = "បញ្ហានយោបាយ"
            response.meta['class_url'] = new_ninth_url
            response.meta['category1'] = category1
            yield scrapy.Request(new_ninth_url, callback=self.parse, meta=response.meta)

        for num_elevth in range(1,49):
            new_elevth_url = f'https://www.vodkhmer.news/category/national/political-issues/good-governance/page/{num_elevth}/'
            category1 = "បញ្ហានយោបាយ"
            response.meta['class_url'] = new_elevth_url
            response.meta['category1'] = category1
            yield scrapy.Request(new_elevth_url, callback=self.parse, meta=response.meta)


    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        abstract = response.meta['abstract']
        body_list = response.xpath('//div[@class="elementor-widget-container"]/p/text()').extract()
        body = '\n'.join(body_list)
        body = body.replace("\u200b", "")
        body = body.replace("\xa0", "")
        if "\n" not in body_list:
                body = abstract +"\n"+body
        if body == "\n":
                body =abstract +"\n"+"N"

        title = response.meta['title']
        abstract = response.meta['abstract']
        images = response.meta['images']
        category1 = response.meta['category1']
        pub_time = response.meta['pub_time']
        item['body'] = body
        item['title'] = title
        item['abstract'] = abstract
        item['images'] = images
        item['category1'] = category1
        item['pub_time'] = pub_time
        yield item
