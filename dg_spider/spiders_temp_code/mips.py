from copy import deepcopy
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
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


import scrapy
import time
from dg_spider.items import NewsItem
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

# check: 林泽佳  pass
# author：刘宇康
class MipsSpider(BaseSpider):
    name = 'mips'
    # allowed_domains = ['mips-mm.org']
    start_urls = ['http://mips-mm.org/']
    website_id = 4321
    language_id = 1765


    def parse(self, response):
        publications = response.xpath('//li[@id="menu-item-2570"]/a/@href').get()
        Agreements = response.xpath('//li[@id="menu-item-2569"]/a/@href').get()
        yield Request(url=publications, callback=self.parse_Resources)
        yield Request(url=Agreements, callback=self.parse_Resources)
    def parse_Resources(self, response):
        response_url = str(response.url)
        flag = True
        a_list = response.xpath('//article')
        if OldDateUtil.time is not None:
            last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(a_list[0].css('time::attr(datetime)').get()[:-6], '%Y-%m-%dT%H:%M:%S'))
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for a in a_list:
                item_link = a.css('h2 a::attr(href)').extract()[0]
                title = a.css('h2 a::text').get()
                abstract = a.css('article p::text').get()
                pub_time = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(a.css('div span a time::attr(datetime)').extract_first()[:-6].strip(), '%Y-%m-%dT%H:%M:%S'))
                images = a.css('article div img::attr(src)').extract()
                if response_url[29:41] == 'publications':
                    meta = {'title': title,
                            'abstract': abstract,
                            'pub_time': pub_time,
                            'category1': 'Resources',
                            'category2': 'Publications',
                            'images': images
                            }
                if response_url[29:31] == 'ca':
                    meta = {'title': title,
                            'abstract': abstract,
                            'pub_time': pub_time,
                            'category1': 'Resources',
                            'category2': 'Ceasefire Agreements',
                            'images': images
                            }
                yield Request(url=item_link, callback=self.parse_page, meta=deepcopy(meta))

        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            OlderPost_link = response.xpath('//nav/div/div/a/@href').get()
            OlderPost = response.xpath('//nav/div/div/a/text()').get()
            if OlderPost == 'Older posts':
                yield scrapy.Request(OlderPost_link, callback=self.parse_Resources)
    def parse_page(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract'] if response.meta['abstract'] is not None else item['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        # body是pdf下载链接
        if item['category2'] == 'Publications':
            item['body'] = 'pdf_link:'+response.css('div .ml-3  a::attr(data-downloadurl)').get()
        if item['category2'] == 'Ceasefire Agreements':
            item['body'] = "".join(response.css('div .su-spoiler-title::text').getall())
        item['images'] = response.meta['images']
        yield item
