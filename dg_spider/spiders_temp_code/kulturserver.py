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

# check:wpf pass
class KulturserverSpider(BaseSpider):  # author：田宇甲
    name = 'kulturserver'  # 这是个小网站，里面没有什么新闻，唯一有文章的地方还没有翻页，就两三篇新闻，但是好像更新的比较快，有写的价值
    website_id = 1747
    language_id = 1898
    start_urls = ['http://kulturserver.de/-/aktuell']  # 大概会抱20个网站就停，但是这是他的上限了
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .news_box'):
            meta = {'title_': i.text.strip('\n').split('\n')[0], 'category1_': 'News',
                    'abstract_': i.text.strip('\n').split(i.text.strip('\n').split('\n')[0])[1].strip(),
                    'images_': [i.img['src']]}
            yield Request('http://kulturserver.de'+i.a['href'], callback=self.check_check, meta=meta)

    def check_check(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .news_box div:nth-child(4)').text.strip().strip('\n')
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = OldDateUtil.get_now_datetime_str()  # 也没有时间
        item['images'] = []  # 新闻无图片
        yield item

