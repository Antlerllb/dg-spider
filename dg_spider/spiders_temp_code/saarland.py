# encoding: utf-8



from scrapy.http.request import Request
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

# author: robot_2233
# check:wpf pass
class SaarlandSpider(BaseSpider):  # 网站新闻很少，只有八十多条
    name = 'saarland'
    website_id = 1706
    language_id = 1898
    start_urls = ['https://www.saarland.de/DE/medien-informationen/informationen/amtliche-bekanntmachungen/amtliche-bekanntmachungen_node.html']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' tbody tr'):
            ssd = i.select_one(' td:nth-child(1)').text.strip('"').strip().split(' ')[0].split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.select_one(' td:nth-child(2)').text.strip(),
                        'time_': time_,
                        'category1_': 'informationen',}
                yield Request(i.a['href'], callback=self.parse_item, meta=meat)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .content.small-12.large-10.columns p')])
        item['abstract'] = soup.select(' .content.small-12.large-10.columns p')[0].text.strip()
        item['pub_time'] = response.meta['time_']
        item['images'] = []
        yield item


