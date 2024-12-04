
# 此文件包含的头文件不要修改
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
from lxml import etree

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
from dg_spider.libs.base_spider import BaseSpider
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
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
# 将爬虫类名和name字段改成对应的网站名
class SggporgSpider(BaseSpider):
    author = "彭海杰"
    name = 'sggporg'
    website_id = 2047  # 网站的id(必填)
    language_id = 2242  # 所用语言的id
    start_urls = ['https://www.sggp.org.vn']


    def parse(self, response):
        link_num = [24, 89, 143, 71, 212, 199, 186, 112]

        category = {
            24:'Chính trị',
            89:'Kinh tế',
            143:'Thế giới',
            71:'Giáo dục',
            212:'Y tế - Sức khỏe',
            199:'Xã hội',
            186:'Văn hóa - Giải trí',
            112:'Pháp luậT'
        }

        for num in link_num:
            for page in range(1,200):
                meta = {}
                meta['category1'] = category[num]
                url = f'https://api.sggp.org.vn/api/morenews-zone-{num}-{page}.html?show_author=1&phrase='
                yield scrapy.Request(url=url, callback=self.category_parse,meta=meta)

    def category_parse(self,response):
        for i in response.json()['data']['contents']:

            meta = {}
            meta['pub_time'] = time.strftime('%Y-%m-%d',time.localtime(i['update_time']))+' 00:00:00'
            meta['category1'] = response.meta['category1']

            meta['title'] = i['title']
            meta['abstract'] = i['description'].strip()[3:-4]
            url = 'https://www.sggp.org.vn'+i['url']

            if OldDateUtil.time==None or OldDateUtil.str_datetime_to_timestamp(meta['pub_time']) >= int(OldDateUtil.time):
                yield scrapy.Request(url=url, meta=meta, callback=self.detail_parse)
            else :
                self.logger.info('时间截止')
                # print('时间截至')


                return
    def detail_parse(self,response):

        item = NewsItem(language_id=self.language_id)
        content = etree.HTML(response.text)
        item['title'] = response.meta['title']
        first = content.xpath('//div[@itemprop="articleBody"]//p/text()')
        first.append(item['title'][0])

        item['body'] = '\n'.join(first)
        item['pub_time'] = response.meta['pub_time']
        item['abstract'] = response.meta['abstract']

        if len(item['body']) == 1:
            x = item['title']
            x.append(item['abstract'])
            item['body'] = '\n'.join(x)


        item['images'] = content.xpath('//div[@class="article__body zce-content-body cms-body"]//img/@src')
        if len(item['images'])==0 :
            item['images'] = None


        item['category1'] = response.meta['category1']
        yield item