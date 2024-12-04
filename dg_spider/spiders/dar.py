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
import json

# check: 魏芃枫
class darSpider(BaseSpider):  # author：田宇甲 我喂自己袋盐 这个爬虫用时25分42秒，打破自己速通记录
    name = 'dar'
    website_id = 1273
    language_id = 1866
    start_urls = ['https://www.dar.gov.ph/articles/news/index.json?p=1']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in json.loads(soup.text)['articles']:
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(i['publishedOn']['timeStamp']['iso']) >= int(OldDateUtil.time):
                meta = {'pub_time_': i['publishedOn']['timeStamp']['iso'], 'title_': i['contents'][0]['title'], 'abstract_': i['contents'][0]['excerpt'], 'images_': i['metadata']['featured-image'], 'category1_': 'News'}
                yield Request('https://www.dar.gov.ph/articles/news/'+str(i['contents'][0]['articleId']), callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(i['publishedOn']['timeStamp']['iso']) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace(response.url.split('p=')[1], str(int(response.url.split('p=')[1])+1)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .article-content').text.strip().strip('\n')
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
