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

class KyodoSpider(BaseSpider):
    author = '王伟任'
    name = 'kyodo'
    website_id = 1995
    language_id = 1963
    start_urls = ['https://www.kyodo.co.jp/release-news/','https://www.kyodo.co.jp/entame/showbiz/','https://www.kyodo.co.jp/life/']
    lan_num = 1
    def parse(self, response):
        for num in range(0, 20):
            time_pre = response.xpath('//div [@class="entry-content"]/div/div[@class="meta"]/text()').extract()
            if time_pre ==[]:
                time_pre = response.xpath(' //div [@class="entry-content c08 clife"]/div/div[2]/text()').extract()[num]
            else:
                time_pre = response.xpath('//div [@class="entry-content"]/div/div[@class="meta"]/text()').extract()[num]
            time_pre = "".join(time_pre)
            time_pre = time_pre.replace("年", ",")
            time_pre = time_pre.replace("月", ",")
            time_pre = time_pre.replace("日", ",")
            time_pre = time_pre.replace("\n", "")
            time_pre = time_pre.replace("\t", "")
            time_pre_cut = time_pre.split(",")
            if time_pre_cut[1] == "1":
                time_pre_cut[1] = "01"
            elif time_pre_cut[1] == "2":
                time_pre_cut[1] = "02"
            elif time_pre_cut[1] == "3":
                time_pre_cut[1] = "03"
            elif time_pre_cut[1] == "4":
                time_pre_cut[1] = "04"
            elif time_pre_cut[1] == "5":
                time_pre_cut[1] = "05"
            elif time_pre_cut[1] == "6":
                time_pre_cut[1] = "06"
            elif time_pre_cut[1] == "7":
                time_pre_cut[1] = "07"
            elif time_pre_cut[1] == "8":
                time_pre_cut[1] = "08"
            elif time_pre_cut[1] == "9":
                time_pre_cut[1] = "09"

            if time_pre_cut[2] == "1":
                time_pre_cut[2] = "01"
            elif time_pre_cut[2] == "2":
                time_pre_cut[2] = "02"
            elif time_pre_cut[2] == "3":
                time_pre_cut[2] = "03"
            elif time_pre_cut[2] == "4":
                time_pre_cut[2] = "04"
            elif time_pre_cut[2] == "5":
                time_pre_cut[2] = "05"
            elif time_pre_cut[2] == "6":
                time_pre_cut[2] = "06"
            elif time_pre_cut[2] == "7":
                time_pre_cut[2] = "07"
            elif time_pre_cut[2] == "8":
                time_pre_cut[2] = "08"
            elif time_pre_cut[2] == "9":
                time_pre_cut[2] = "09"
            pub_time = f'{time_pre_cut[0]}-{time_pre_cut[1]}-{time_pre_cut[2]} 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            title = response.xpath('///div [@class="entry-content"]/div/h2/a/text()').extract()
            if title == []:
                title = response.xpath('//div [@class="entry-content c08 clife"]/div/h2/a/text()').extract()[num]
            else:
                title = response.xpath('///div [@class="entry-content"]/div/h2/a/text()').extract()[num]
            title = ''.join(title)
            title = title.replace("\r\n", "")
            title = title.replace("\r", "")
            title = title.replace("\t", "")
            title = title.replace("\u200b", "")
            title = title.replace("\u202f", "")
            title = title.replace("\u3000", "")
            title = title.replace("\xa0", "")
            title = title.replace("\n", "")

            abstract = response.xpath('//div [@class="entry-content"]/div/p/text()').extract()
            if abstract ==[]:
                abstract = response.xpath(f'//*[@id="Main"]/div[2]/div[{num+1}]/div/text()').extract()
            else:
                abstract = response.xpath('//div [@class="entry-content"]/div/p/text()').extract()[num]
            abstract = ''.join(abstract)

            abstract = abstract.replace("\r", "")
            abstract = abstract.replace("\t", "")
            abstract = abstract.replace("\u200b", "")
            abstract = abstract.replace("\u202f", "")
            abstract = abstract.replace("\u3000", "")
            abstract = abstract.replace("\xa0", "")
            abstract = abstract.replace("\n", "")

            website_href = response.xpath('//div [@class="entry-content"]/div/h2/a/@href').extract()
            if website_href ==[]:
                website_href = response.xpath('//div [@class="entry-content c08 clife"]/div/h2/a/@href').extract()[num]
            else:
                website_href = response.xpath('//div [@class="entry-content"]/div/h2/a/@href').extract()[num]

            response.meta['pub_time'] = pub_time
            response.meta['title'] = title
            response.meta['abstract'] = abstract
            yield scrapy.Request(website_href, callback=self.parse_item, meta=response.meta)
            if "release-news" in website_href:
                for page_num in range(2,50):
                    next_url =f'https://www.kyodo.co.jp/release-news/page/{page_num}/'
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            if "entame" in website_href:
                for page_num in range(2, 40):
                    next_url = f'https://www.kyodo.co.jp/entame/showbiz/page/{page_num}/'
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
            else:
                for page_num in range(2, 70):
                    next_url = f'https://www.kyodo.co.jp/life/page/{page_num}/'
                    yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)


    def parse_item(self,response):

        item = NewsItem(language_id=self.language_id)
        pub_time = response.meta['pub_time']
        abstract = response.meta['abstract']
        title = response.meta['title']
        images = response.xpath('//div [@class="entry-content c04"]/div/img/@src').extract()
        if images ==[]:
            images = response.xpath('//div [@class="entry-content c02"]/p/img/@src').extract()
        if images =='':
            images = response.xpath('//div [@class="entry-content c02"]/p/img/@src').extract()
        if images ==[]:
            images = response.xpath('//div [@class="entry-content c02"]/div/a/img/@src').extract()
        if images =='':
            images = response.xpath('//div [@class="entry-content c02"]/div/a/img/@src').extract()
        if images == []:
            images = response.xpath(' //div [@class="entry-content "]/p/img/@src').extract()
        if images == '':
            images = response.xpath(' //div [@class="entry-content "]/p/img/@src').extract()


        body_list = response.xpath('//div [@class="entry-content c04"]/p/text()').extract()
        if body_list == []:
            body_list = response.xpath('//div [@class="entry-content c02"]/p/text()').extract()
        if body_list == '':
            body_list = response.xpath('//div [@class="entry-content c02"]/p/text()').extract()
        if body_list == []:
            body_list = response.xpath('//div [@class="entry-content "]/p/text()').extract()
        if body_list == '':
            body_list = response.xpath('//div [@class="entry-content "]/p/text()').extract()
        body = '\n'.join(body_list)
        body = body.replace("\u200b", "")
        body = body.replace("\u202f", "")
        body = body.replace("\u3000", "")
        body = body.replace("\xa0", "")

        if "\n" not in body_list:
            body = abstract + "\n" + body
        if body == "\n":
            body = abstract + "\n" + "N"

        category1 ="ニュース"
        item['body'] = body
        item['title'] = title
        item['abstract'] = abstract
        item['images'] = images
        item['category1'] = category1
        item['pub_time'] = pub_time

        yield item

