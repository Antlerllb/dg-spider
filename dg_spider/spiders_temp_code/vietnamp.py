
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
class VietnampSpider(BaseSpider):
    author = "彭海杰"
    name = 'vietnamp'
    website_id = 2043  # 网站的id(必填)
    language_id = 2242  # 所用语言的id
    start_urls = ['https://www.vietnamplus.vn']


    def parse(self, response):
        link_num = [205,1155,1307,1315,1322,984,1129,820,946,1321,1309]

        category = {
            1322:'CƠN BÃO SỐ 3(SIÊU BÃO YAGI)',
            1321:'TỔNG BÍ THƯ NGUYỄN PHÚ TRỌNG',
            984:'CĂNG THẲNG NGA - UKRAINE',
            1309:'VỤ VẠN THỊNH PHÁT',
            205:'BIỂN ĐÔNG',
            1129:'XUNG ĐỘT ISRAEL - HAMAS',
            1155:'VỤ VIỆT Á',
            1307:'BẢO VỆ NỀN TẢNG TƯ TƯỞNG CỦA ĐẢNG',
            820:'XÂY DỰNG ĐẢNG',
            1315:'CĂNG THẲNG IRAN - ISRAEL',
            946:'CHỐNG THAM NHŨNG',
        }

        for num in link_num:
            for page in range(1,75):
                meta = {}
                meta['category1'] = category[num]
                url = f'https://apiv3.vietnamplus.vn/api/morenews-topic-{num}-{page}.html?phrase=&page_size=30'
                yield scrapy.Request(url=url, callback=self.category_parse,meta=meta)

    def category_parse(self,response):
        for i in response.json()['data']['contents']:

            meta = {}
            meta['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(i['date']))
            # print(meta['pub_time'])
            # print(i['date'])
            meta['category1'] = response.meta['category1']

            meta['title'] = i['title']
            meta['abstract'] = i['description'].strip()[3:-4]
            url = 'https://www.vietnamplus.vn'+i['url']

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


        item['images'] = []
        for i in content.xpath('//figure/img/@src'):
            if i[0]=='h':
                item['images'].append(i)

        if len(item['images'])==0 :
            item['images'] = None


        item['category1'] = response.meta['category1']
        yield item