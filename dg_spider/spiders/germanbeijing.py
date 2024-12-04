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


# 这个网站只有五页，其他的应该是网站没放出来
class germanbeijingSpider(BaseSpider):  # author：田宇甲
    name = 'germanbeijing'
    website_id = 1795
    language_id = 1898
    start_urls = [f'http://german.beijingreview.com.cn/{i}/index.html' for i in ['International', 'China', 'Wirtschaft', 'Kultur', 'Meinungen']]
    # proxy = '02'
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' body div:nth-child(3) ul li')[0:9]:
            ssd = i.select_one(' .lmm').text.strip().split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_, 'title_': i.div.table.text.strip().split('\n\n\n\n')[0], 'abstract_': i.div.table.text.strip().split('\n\n\n\n')[1], 'category1_': response.url.split('/index')[0].split('.cn/')[1], 'images_': [response.url.split('/index')[0]+str(i).split('src=".')[1].split('"')[0]]}
                yield Request(response.url.split('/index')[0]+str(i).split('href=".')[1].split('"')[0], callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            if r'/index_' not in response.url:
                url = 'http://german.beijingreview.com.cn/'+response.url.split('/index')[0].split('.cn/')[1]+'/index_1.html'
                yield Request(url)
            else:
                page = int(response.url.strip('.html').split('_')[1])
                url = response.url.split('index_')[0]+'index_'+str(page+1)+'.html'
                yield Request(url)

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
