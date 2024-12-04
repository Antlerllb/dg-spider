from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import json


# Author:田宇甲
class JabarSpider(BaseSpider):
    name = 'jabar'#动态
    website_id = 36
    language_id = 1952
    start_urls = ["https://jabar.tribunnews.com/ajax/latest?start=0",
                  "https://jabar.tribunnews.com/ajax/latest_section?&section=22&section_name=kesehatan&start=0",
                  "https://jabar.tribunnews.com/ajax/latest_section?&section=17&section_name=travel&start=0",
                  "https://tribunjabartravel.tribunnews.com/ajax/latest_section?&section=1&start=0"]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in json.loads(soup.text)['posts']:
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(i['date'].split('+')[0].replace('T', ' ')) + 3200 >= int(OldDateUtil.time):
                meta = {'pub_time_': i['date'].split('+')[0].replace('T', ' '), 'title_': i['title'], 'abstract_': i['introtext'], 'images_': i['thumb'], 'category1_': 'news'}
                yield Request(i['url'], callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(i['date'].split('+')[0].replace('T', ' ')) + 3200 >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            tyj = str(response.url).split('start=')[0]+'start='+str(int(str(response.url).split('start=')[-1])+20)
            yield Request(tyj)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = '\n'.join(i.text for i in soup.select(' .side-article.txt-article.multi-fontsize'))
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        return item