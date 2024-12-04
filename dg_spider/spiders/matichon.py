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

# author:robot-2233   这个网站有时候会在列表里的新闻删了但是还在列表里，所以会抱一点404，正常
class matichonSpider(BaseSpider):
    name = 'matichon'
    website_id = 232
    language_id = 2208
    start_urls = ['https://www.matichon.co.th/']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' #menu-main-menu2-1 li')[1:]:
            if 'sub-menu' in str(i):
                pass
            elif './' in i.a['href']:
                meat = {'category1_': i.a['href'].split('./')[1] if i.a['href'].count('/') == 4 else i.a['href'].split('./')[1].split('/')[0],
                        'category2_': None if i.a['href'].count('/') == 4 else i.a['href'].split('./')[1].split('/')[1] if '%' not in i.a['href'] else 'เรียงคน-ภาพข่าวสังคม'}
                yield Request(i.a['href'], callback=self.RUN, meta=meat)

    def RUN(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if 'page' not in response.url:
            for i in soup.select(' .td-category-grid.td-container-wrap .td-block-row .td-block-span6 .item-details'):
                time_ = str(i.time).split('datetime="')[1].split('"')[0].split('+')[0].replace('T', ' ')
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    response.meta['title_'] = i.h3.text
                    response.meta['abstract_'] = i.select_one(' .td-excerpt').text
                    response.meta['time_'] = time_
                    yield Request(i.h3.a['href'], callback=self.parse_item, meta=response.meta)
        for i in soup.select(' .td_module_10.td_module_wrap.td-animation-stack .item-details'):
            time_ = str(i.time).split('datetime="')[1].split('"')[0].split('+')[0].replace('T', ' ')
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                response.meta['title_'] = i.h3.text
                response.meta['abstract_'] = i.select_one(' .td-excerpt').text
                response.meta['time_'] = time_
                yield Request(i.h3.a['href'], callback=self.parse_item, meta=response.meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if 'page' not in response.url:
                yield Request(response.url+'/page/2', callback=self.RUN, meta=response.meta)
            else:
                yield Request(response.url.replace('page/'+response.url.split('page/')[1], 'page/'+str(int(response.url.split('page/')[1])+1)), callback=self.RUN, meta=response.meta)


    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = response.meta['category2_']
        item['body'] = soup.select_one(' .td-post-content').text.strip().strip('\n')
        item['abstract'] = response.meta['abstract_'].strip().strip('.')
        item['pub_time'] = response.meta['time_']
        item['images'] = soup.select_one(' .td-post-featured-image a')['href']
        yield item

