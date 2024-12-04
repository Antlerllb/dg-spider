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

class germanchinatodaySpider(BaseSpider): # author：田宇甲
    name = 'germanchinatoday'
    website_id = 1793
    language_id = 1898
    start_urls = [f'http://german.chinatoday.com.cn/ch/{i}/' for i in ['aufmacher','aktuelles','politik','wirtschaft','gesellschaft','nachrichten_im_bild','bildung_kultur_und_reisen']]
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .CT_CLBox .CT_WenList .CT_CLLiBox div')[::2]:
            time_ = i.span.text.split(', ')[-1]+'-'+i.span.text.split(', ')[1]+i.span.text.split(', ')[0]+':00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_, 'title_': i.a.text, 'abstract_': i.p.text,  'category1_': response.url.split('ch/')[1].split('/')[0], 'images_': [('http://german.chinatoday.com.cn/ch/'+response.url.split('ch/')[1].split('/')[0]+i.img['src'].strip('.') if len(i.img['src']) > 3 else '')]}
                yield Request('http://german.chinatoday.com.cn/ch/'+response.url.split('ch/')[1].split('/')[0]+i.a['href'].strip('.'), callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if 'index' not in response.url:
                yield Request(response.url+'index_1.html')
            else:
                page = int(response.url.strip('.html').split('index_')[1])
                yield Request(response.url.strip('.html').strip(str(page))+str(page+1)+'.html')

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .TRS_Editor').text.strip().strip('\n')
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item