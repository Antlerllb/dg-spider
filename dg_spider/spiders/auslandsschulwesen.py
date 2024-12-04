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

# check: wpf pass
# author: robot_2233

class AuslandsschulwesenSpider(BaseSpider):  # 全在一个页面
    name = 'auslandsschulwesen'
    website_id = 1755
    language_id = 1898
    start_urls = ['https://www.auslandsschulwesen.de/Webs/ZfA/DE/Die-ZfA/Meldungen/meldungen_node.html;jsessionid=C1891C8A236677D695321F984DD4F383.intranet242D1']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .textualData.links tbody tr'):
            ssd = i.select_one(' td:nth-child(1)').text.strip().split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.select_one(' .RichTextIntLink').text.strip('\n'),
                        'time_': time_,
                        'category1_': 'Auslandsschulwesen',
                        'abstract_': i.select_one(' .odd p:nth-child(3)').text.strip(),
                        'images_': [i.img['src']]}
                yield Request('https://www.auslandsschulwesen.de/'+i.select_one(' .RichTextIntLink')['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace('.intranet242D' + response.url.split('.intranet242D')[1], '.intranet242D' + str(int(response.url.split('.intranet242D')[1]) + 1)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = ''.join([i.text for i in soup.select(' .l-content-article p')])
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = response.meta['images_']
        yield item


