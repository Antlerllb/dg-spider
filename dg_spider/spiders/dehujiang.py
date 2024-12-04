# encoding: utf-8



from scrapy.http.request import Request
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
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# check:wpf pass
# author: 田宇甲
class DehujiangSpider(BaseSpider):  # 一个简单的静态爬虫，到底了就会报错然后停下来，分了article和news两种新闻都可以爬。
    name = 'dehujiang'
    website_id = 1798
    language_id = 1814
    start_urls = ['https://de.hujiang.com/new/xiaoyuan/']

    def parse(self, response):  # 留学咨讯新闻，怪怪的，也不多，但是能写就写了
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .m-lists .list-item'):
            time_ = i.select_one(' .info .tag').text + ':00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.select_one(' .list-item-title').text.strip('\n'), 'time_': time_, 'category1_': '留学资讯', 'abstract_': i.select_one(' .list-item-desc').text}
                yield Request('https://de.hujiang.com'+i.select_one(' a:nth-child(2)')['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if 'page' not in response.url:
                yield Request(response.url + '/page2/')
            else:
                yield Request(self.start_urls[0]+'/page'+str(int(response.url.split('/page')[1].strip('/'))+1)+'/')

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .article-content p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = []
        yield item


