import re

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
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from scrapy import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil




# author 刘鼎谦
class NewsduanSpider(BaseSpider):
    api = 'http://www.newsduan.com/newsyun/dynamicList/getdynamicListForWapBBZTContentList.jspx?orderBy=2&pageIndex={}&channelId=2441&channelPageSize=5'

    name = 'newsduan'
    # allowed_domains = ['newsduan.com/newsyun/lwzxw/']
    start_urls = ['http://www.newsduan.com/newsyun/dynamicList/getdynamicListForWapBBZTContentList.jspx?orderBy=2&pageIndex=1&channelId=2441&channelPageSize=5'
]

    website_id = 1669
    language_id = 1002

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in [a.get('href') for a in soup.select('a')]:
            yield Request(url=i, callback=self.parse_item)
        try:
            if response.meta['page']:
                response.meta['page'] +=1
        except:
            response.meta['page'] = 2
        if OldDateUtil.time is not None:
            last_pub = re.findall('\d+-\d+-\d+',soup.select('.has_img_time')[-1].text)[0] +' 00:00:00' if soup.select('.has_img_time') else OldDateUtil.get_now_datetime_str()
            if OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(last_pub):
                yield Request(url=NewsduanSpider.api.format( response.meta['page']),meta=response.meta)
            else:
                self.logger.info('时间截止')
        else:
            yield Request(url=NewsduanSpider.api.format(response.meta['page']), meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['title'] = soup.select_one('h1').text
        item['category1'] = 'news'
        item['category2'] = None
        item['body'] = '\n'.join([i.text.strip(' \n,▲') for i in soup.select('.p_con p') ])
        item['abstract'] = item['title']
        item['pub_time'] = soup.select('.sdata span')[-1].text+':00'
        item['images'] = ['http://www.newsduan.com'+i.get('src') for i in soup.select('.p_con img')]
        yield item
