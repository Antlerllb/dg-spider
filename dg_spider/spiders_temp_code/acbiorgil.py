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
from datetime import datetime
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


class AcbiorgilSpider(BaseSpider):
    name = 'acbiorgil'
    allowed_domains = ['acbi.org.il']
    start_urls = ['https://www.acbi.org.il/blog/']

    website_id = 1929
    language_id = 1813
    custom_settings = {'DOWNLOAD_TIMEOUT': 100}
    proxy = '02'

    def parse(self, response):
        section_obj_list = response.css('section.post')
        for section_obj in section_obj_list:
            meta = {'category1': '活动新闻',
                    'title':section_obj.css('h2 a::text').extract_first().strip(),
                    'abstract': section_obj.css('div.col-md-8 > p::text').extract_first().strip(),
                    'pub_time': time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(section_obj.css('p.date-comments').xpath('string(.)').extract_first().strip(),'%m/%d/%Y')),
                    }
            item_link = 'https://www.acbi.org.il' + section_obj.css('h2 a::attr(href)').extract_first().strip()
            yield scrapy.Request(item_link, callback=self.parse_item, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['abstract'] = response.meta['abstract'] if response.meta['abstract'] != '' else item['title']
        item['body'] = '\n'.join([i.strip() for i in response.css('div#post-content p').xpath('string(.)').extract() if i.strip() != ''])
        item['images'] = ['https://www.acbi.org.il'+i for i in response.css('div#post-content p img::attr(src)').extract()]
        yield item

