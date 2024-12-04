# #-*- coding: utf-8 -*-
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





from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
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


class JpbankjapanpostSpider(BaseSpider):
    author = '王伟任'
    name = 'jpbankjapanpost'
    website_id = 2213
    language_id = 1963
    lan_num = 1
    start_urls = ['https://www.jp-bank.japanpost.jp/news/2023/news_2023.html',
                  'https://www.jp-bank.japanpost.jp/news/2022/news_2022.html',
                  'https://www.jp-bank.japanpost.jp/news/2021/news_2021.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2023/abt_prs_2023.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2022/abt_prs_2022.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2021/abt_prs_2021.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2020/abt_prs_2020.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2019/abt_prs_2019.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2018/abt_prs_2018.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2017/abt_prs_2017.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2016/abt_prs_2016.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2015/abt_prs_2015.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2014/abt_prs_2014.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2013/abt_prs_2013.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2012/abt_prs_2012.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2011/abt_prs_2011.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2010/abt_prs_2010.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2009/abt_prs_2009.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2008/abt_prs_2008.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2007/abt_prs_2007.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2006/abt_prs_2006.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2005/abt_prs_2005.html',
                  'https://www.jp-bank.japanpost.jp/aboutus/press/2004/abt_prs_2004.html',]

    def parse(self, response):

        href_list = response.xpath(
            '//dl[@class="dl_news clfx"]/dd [@class="dd_txt"]/p/a/@href').extract()

        for href in href_list:
            add_href= 'https://www.jp-bank.japanpost.jp'+href

            response.meta['add_href'] =add_href
            yield scrapy.Request(add_href, callback=self.parse_item, meta=response.meta)
    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        add_href =response.meta['add_href']
        time_pre=response.xpath('//div/div/h3[1]/text()').extract_first()

        time_pre =time_pre.replace('年','-')
        time_pre = time_pre.replace('月', '-')
        time_pre = time_pre.replace('日', ' ')
        pub_time =time_pre+'00:00:00'

        if OldDateUtil.time is not None and  OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
            return

        images =[]
        category1=response.xpath('//div/div/h2/text()').extract_first()
        if category1== 'お知らせ':
            category1 = response.xpath('//div/div/div/h2/text()').extract_first()
        title =response.xpath('//div/div/h3[2]/text()').extract_first()
        title = ''.join(title)
        title = title.replace("\u200b", "")
        title = title.replace("\xa0", "")
        title = title.replace("\u3000", "")
        title = title.replace("\r", "")
        title = title.replace("\t", "")
        abstract = response.xpath('//div [@class="txt_align_l"]/p[1]/text()').extract_first()
        abstract = ''.join(abstract)
        if abstract=='':
            abstract = response.xpath('//div [@class="txt_align_l"]/p[2]/text()').extract_first()
        if abstract=='&nbsp;':
            abstract = response.xpath('//div [@class="txt_align_l"]/p[2]/text()').extract_first()
        if abstract==None:
            abstract = response.xpath('//div [@class="txt_align_l"]/p[2]/text()').extract_first()
        if abstract==[]:
            abstract = response.xpath('//div [@class="txt_align_l"]/p[2]/text()').extract_first()
        if len(abstract) <=4:
            abstract = response.xpath('//div [@class="txt_align_l"]/p[2]/text()').extract_first()
        abstract = ''.join(abstract)
        if abstract=='':
            abstract = response.xpath('//div [@class="txt_align_l"]/p[3]/text()').extract_first()
        if abstract=='&nbsp;':
            abstract = response.xpath('//div [@class="txt_align_l"]/p[3]/text()').extract_first()
        if abstract==None:
            abstract = response.xpath('//div [@class="txt_align_l"]/p[3]/text()').extract_first()
        if abstract==[]:
            abstract = response.xpath('//div [@class="txt_align_l"]/p[3]/text()').extract_first()
        if len(abstract) <=4:
            abstract = response.xpath('//div [@class="txt_align_l"]/p[3]/text()').extract_first()
        abstract = ''.join(abstract)
        if abstract=='':
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[1]/text()').extract_first()
        if abstract=='&nbsp;':
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[1]/text()').extract_first()
        if abstract==None:
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[1]/text()').extract_first()
        if abstract==[]:
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[1]/text()').extract_first()
        if len(abstract) <=4:
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[1]/text()').extract_first()
        abstract = ''.join(abstract)
        if abstract=='':
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[2]/text()').extract_first()
        if abstract=='&nbsp;':
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[2]/text()').extract_first()
        if abstract==None:
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[2]/text()').extract_first()
        if abstract==[]:
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[2]/text()').extract_first()
        if len(abstract) <=4:
            abstract = response.xpath('//div [@class="txt_align_l"]/p/span[2]/text()').extract_first()
        abstract = ''.join(abstract)
        abstract = abstract.replace("\u200b", "")
        abstract = abstract.replace("\xa0", "")
        abstract = abstract.replace("\u3000", "")
        abstract = abstract.replace("\r", "")
        abstract = abstract.replace("\t", "")
        abstract = abstract.replace("\n", "")
        abstract = abstract.replace(" ", "")
        abstract = abstract +'N'


        body = response.xpath('//div [@class="txt_align_l"]/p/text()').extract()
        body = '\n'.join(body)
        body = body.replace("\u200b", "")
        body = body.replace("\xa0", "")
        body = body.replace("\u3000", "")
        body = body.replace("\r", "")
        body = body.replace("\t", "")
        if "\n" not in body:
                body = abstract +"\n"+body
        if body == "\n":
            body =abstract +"\n"+"N"



        item['title'] = title
        item['body'] = body
        item['abstract'] = abstract
        item['images'] = images
        item['category1'] = category1
        item['pub_time'] = pub_time


        yield item


