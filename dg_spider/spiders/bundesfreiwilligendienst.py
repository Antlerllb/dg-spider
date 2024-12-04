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

# check: wpf pass
class BundesfreiwilligendienstSpider(BaseSpider):  # author：田宇甲 这个网站只有一页文章，而且是关于志愿的报道，比较少，但是有时间，而且会更新
    name = 'bundesfreiwilligendienst'
    website_id = 1746
    language_id = 1898
    start_urls = ['https://www.bundesfreiwilligendienst.de/servicemenue/archiv']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' #content .news-list-view div')[::3]:  # 有的不是新闻
            try:
                ssd = i.select_one(' .news-list-date').text.strip().split('.')
                time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    if 'downloads' not in i.a['href']:
                        meta = {'pub_time_': time_, 'title_': i.h2.text,  'category1_': 'Archiv'}
                        yield Request('https://www.bundesfreiwilligendienst.de'+i.a['href'], callback=self.parse_item, meta=meta)
            except:
                pass

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        try:
            item['body'] = soup.select_one(' .csc-textpic-text').text.strip().strip('\n')
            item['abstract'] = soup.select_one(' .csc-textpic-text').text.strip().strip('\n').split('\n')[0]
        except:
            try:
                item['body'] = soup.select_one(' .ce-bodytext').text.strip().strip('\n')
                item['abstract'] = soup.select_one(' .ce-bodytext').text.strip().strip('\n')
            except:
                item['body'] = soup.select_one(' #content').text.strip().strip('\n')
                item['abstract'] = soup.select_one(' #content').text.strip().strip('\n').split('\n')[0]
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = []
        yield item
