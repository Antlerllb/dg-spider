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

class BamfSpider(BaseSpider):  # 新闻量比较少
    name = 'bamf'
    website_id = 1744
    language_id = 1898
    start_urls = ['https://www.bamf.de/SiteGlobals/Forms/Suche/Expertensuche_Formular.html?cl2Categories_Typ=meldung&sortOrder=dateOfIssue_dt+desc&pageLocale=de&gtp=296874_list%253D1']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .l-results__content .l-results__result.c-teaser.c-teaser--row'):
            ssd = i.select_one(' .c-meta__item').text.strip().strip('"').split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meat = {'title_': i.select_one(' .c-teaser__heading a').text.strip('\n'),
                        'time_': time_,
                        'category1_': 'Search',
                        'abstract_': i.select_one(' .c-teaser__text.c-teaser__text--column p').text.strip(),
                        'images_': ['https://www.bamf.de/'+i.img['src']]}
                yield Request('https://www.bamf.de/'+i.select_one(' .c-teaser__heading a')['href'], callback=self.parse_item, meta=meat)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield Request(response.url.replace('_list%253D' + response.url.split('_list%253D')[1], '_list%253D' + str(int(response.url.split('_list%253D')[1]) + 1)))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .column.small-12.large-8').text.strip()
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = response.meta['images_']
        yield item


