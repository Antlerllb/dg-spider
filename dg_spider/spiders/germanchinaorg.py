from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

class germanchinaorgSpider(BaseSpider): # author：田宇甲 这个网站只有十页，以前的新闻网站获取不到了,新闻可能会比较少
    name = 'germanchinaorg'
    website_id = 1792
    language_id = 1898
    start_urls = [f'http://german.china.org.cn/node_{i}.htm' for i in ['7227460','7227461','7227463','7227462','7227464','7227465','7227466']]
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .main ul li'):
            time_ = i.h1.a['href'].split('/txt/')[1].split('/c')[0].replace('/','-')+' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_, 'title_': i.h1.text, 'abstract_': i.p.text,  'category1_': 'Interview'}
                yield Request(i.h1.a['href'], callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if response.url.count("_") == 1:
                yield Request(response.url.strip('.htm')+'_2.htm')
            else:
                page = int(response.url.strip('.htm').split('_')[1])
                yield Request(response.url.strip('.htm').strip(str(page))+str(page+1)+'.htm')

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .content1').text.strip().strip('\n')
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        try:
            item['images'] = [soup.select_one(' .content1 img')['src']]
        except:
            item['images'] = []
        yield item
