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

class PostkhmerSpider(BaseSpider):
    author = '王伟任'
    name = 'postkhmer'
    website_id = 2685
    language_id = 2275
    start_urls = ['https://www.postkhmer.com/national?page=1']
    lan_num = 1


    def parse(self, response):
        item = NewsItem(language_id=self.language_id)
        for num in range(2,12):

            pre_new_url = response.xpath(f'//div [@class="main-category-contents"]/div/div[{num}]/div/a/@href').extract_first()
            new_url = 'https://www.postkhmer.com'+str(pre_new_url)
            response.meta['new_url'] = new_url

            title = response.xpath(f'//div [@class="main-category-contents"]/div/div[{num}]/h3/a/text()').extract_first()
            title = str(title)
            title = title.replace('\u200b','')

            abstract = response.xpath(f'//div [@class="main-category-contents"]/div/div[{num}]/div[@class="summary"]/p/text()[2]').extract_first()
            if abstract == None:
                abstract = response.xpath(
                    f'//div [@class="main-category-contents"]/div/div[{num}]/div[@class="summary"]/p/text()').extract_first()
            abstract = "".join(abstract)
            abstract = abstract.replace("\u200b", "")
            abstract =  abstract.replace("\xa0", "")
            abstract =  abstract.replace("\n", "")

            images = response.xpath(f'//div [@class="main-category-contents"]/div/div[{num}]/div/a/img/@src').extract()

            category1 = 'ព័ត៌មានជាតិ'
            prev_pub_time_list = response.xpath(f'//div [@class="main-category-contents"]/div/div[{num}]/div [@class="posted-date"]/text()').extract_first().split(' ')
            year_time = prev_pub_time_list[4]


            A = 'January'
            B = 'February'
            C = 'March'
            D = 'April'
            E = 'May'
            F = 'June'
            G = 'July'
            H = 'August'
            I = 'September'
            J = 'October'
            K = 'November'
            L = 'December'
            if prev_pub_time_list[2] == A:
                prev_pub_time_list[2] = '01'
            elif prev_pub_time_list[2] == B:
                prev_pub_time_list[2] = '02'
            elif prev_pub_time_list[2] == C:
                prev_pub_time_list[2] = '03'
            elif prev_pub_time_list[2] == D:
                prev_pub_time_list[2] = '04'
            elif prev_pub_time_list[2] == E:
                prev_pub_time_list[2] = '05'
            elif prev_pub_time_list[2] == F:
                prev_pub_time_list[2] = '06'
            elif prev_pub_time_list[2] == G:
                prev_pub_time_list[2] = '07'
            elif prev_pub_time_list[2] == H:
                prev_pub_time_list[2] = '08'
            elif prev_pub_time_list[2] == I:
                prev_pub_time_list[2] = '09'
            elif prev_pub_time_list[2] == J:
                prev_pub_time_list[2] = '10'
            elif prev_pub_time_list[2] == K:
                prev_pub_time_list[2] = '11'
            elif prev_pub_time_list[2] == L:
                prev_pub_time_list[2] = '12'
            month_time = prev_pub_time_list[2]

            date_pre = str(prev_pub_time_list[3])
            date_pre_cut = date_pre.split(",")
            if date_pre_cut[0] =='1':
                date_pre_cut[0] ='01'
            elif date_pre_cut[0] == '2':
                date_pre_cut[0] ='02'
            elif date_pre_cut[0] == '3':
                date_pre_cut[0] ='03'
            elif date_pre_cut[0] == '4':
                date_pre_cut[0] ='04'
            elif date_pre_cut[0] == '5':
                date_pre_cut[0] ='05'
            elif date_pre_cut[0] == '6':
                date_pre_cut[0] ='06'
            elif date_pre_cut[0] == '7':
                date_pre_cut[0] ='07'
            elif date_pre_cut[0] == '8':
                date_pre_cut[0] ='08'
            elif date_pre_cut[0] == '9':
                date_pre_cut[0] ='09'
            date_time = date_pre_cut[0]
            look_am_or_pm = prev_pub_time_list[7]
            hour_min_time = prev_pub_time_list[6]
            hour_min_time_clear = hour_min_time.split(':')
            if hour_min_time_clear[0] =='1':
                hour_min_time_clear[0] ='01'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '13'
            elif hour_min_time_clear[0] == '2':
                hour_min_time_clear[0] ='02'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '14'
            elif hour_min_time_clear[0] == '3':
                hour_min_time_clear[0] ='03'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '15'
            elif hour_min_time_clear[0] == '4':
                hour_min_time_clear[0] ='04'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '16'
            elif hour_min_time_clear[0] == '5':
                hour_min_time_clear[0] ='05'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '17'
            elif hour_min_time_clear[0] == '6':
                hour_min_time_clear[0] ='06'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '18'
            elif hour_min_time_clear[0] == '7':
                hour_min_time_clear[0] ='07'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '19'
            elif hour_min_time_clear[0] == '8':
                hour_min_time_clear[0] ='08'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '20'
            elif hour_min_time_clear[0] == '9':
                hour_min_time_clear[0] ='09'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '21'
            elif hour_min_time_clear[0] == '10':
                hour_min_time_clear[0] ='10'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '22'
            elif hour_min_time_clear[0] == '11':
                hour_min_time_clear[0] ='11'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '23'
            elif hour_min_time_clear[0] == '12':
                hour_min_time_clear[0] ='12'
                if look_am_or_pm =='pm':
                    hour_min_time_clear[0] = '00'
            hour_time = hour_min_time_clear[0]
            min_time = hour_min_time_clear[1]
            pub_time =f'{year_time}-{month_time}-{date_time} {hour_time}:{min_time}:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            response.meta['title'] = title
            response.meta['abstract'] = abstract
            response.meta['images'] = images
            response.meta['category1'] = category1
            response.meta['pub_time'] = pub_time


            yield scrapy.Request(new_url, callback=self.parse_item, meta=response.meta)
        for page_num_two in range(2, 411):
            the_next_url = f'https://www.postkhmer.com/national?page={page_num_two}'
            response.meta['the_next_url'] = the_next_url
            yield scrapy.Request(the_next_url, callback=self.parse, meta=response.meta)

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        abstract = response.meta['abstract']

        body_list = response.xpath('/html/body/div[3]/div/div[5]/div[1]/div[1]/article/div/div/div[4]/p[2]/text()').extract()
        if body_list ==[]:
            body_list = response.xpath('/html/body/div[3]/div/div[5]/div[1]/div[1]/article/div/div/div[4]/p[3]/text()').extract()
            if body_list == []:
                body_list = response.xpath(
                    '/html/body/div[3]/div/div[5]/div[1]/div[1]/article/div/div[4]/p/text()').extract()

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

