# encoding: utf-8
from copy import deepcopy



import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from datetime import datetime, timedelta
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# author：欧炎镁
class JpostcomSpider(BaseSpider):
    name = 'jpostcom'
    allowed_domains = ['jpost.com']
    start_urls = ['https://www.jpost.com/articlearchive/listarticlearchive.aspx']
    website_id = 1930
    language_id = 1866
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD' :"TLSv1.2",'RETRY_TIMES':10,'DOWNLOAD_DELAY':0.1,'RANDOMIZE_DOWNLOAD_DELAY':True}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',}
    proxy = '02'

    def parse(self, response):
        flag = True
        li_obj_list = response.css('li.Archive-feed-item')
        if li_obj_list:
            if OldDateUtil.time is not None:
                last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(li_obj_list.css('p.article-date-time').xpath('string(.)').extract()[0].strip(),'%m/%d/%Y %I:%M:%S %p'))
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                for li_obj in li_obj_list:
                    meta = {'abstract': li_obj.css('div.archive-teaser').xpath('string(.)').extract_first().strip(),
                            'title': li_obj.css('a.title').xpath('string(.)').extract_first().strip(),
                            'pub_time': time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(li_obj.css('p.article-date-time').xpath('string(.)').extract_first().strip(),'%m/%d/%Y %I:%M:%S %p'))
                            }
                    item_link = li_obj.css('a.title::attr(href)').extract_first()
                    yield scrapy.Request(url=item_link, callback=self.parse_item, meta=deepcopy(meta),headers=self.headers)
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:
                thispage_time = response.url.split('=')[1] if len(response.url.split('=')) > 1 else datetime.today().strftime('%m/%d/%Y')
                for i in [1,-1,-2]:  # 请求前一天和后两天，防止前一天没请求到，防止后一天没请求到导致停止
                    date_it = (datetime.strptime(thispage_time, "%m/%d/%Y") + timedelta(days=i))
                    if OldDateUtil.time is None or datetime.date(date_it) >= datetime.date(datetime.fromtimestamp(OldDateUtil.time)): # 如果self.time存在，只拿大于或等于这个时间的新闻
                        yield scrapy.Request(response.url.split('?')[0] + '?date=' + date_it.strftime('%m/%d/%Y'),callback=self.parse, headers=self.headers)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = ','.join(response.css('a.tag::text').extract())
        item['category2'] = None
        item['body'] = '\n'.join([i.strip() for i in response.css('div[class^=article-inner-content] >*:not(div):not(script):not(template):not([class=article-image-in-body])').xpath('string(.)').extract() if i.strip() != '' and '(credit:' not in i])
        item['abstract'] = response.meta['abstract'] if response.meta['abstract'] != '' else item['title']
        item['images'] = response.css('img.article-image-element,div.article-image-in-body img').css('::attr(src)').extract()
        yield item

