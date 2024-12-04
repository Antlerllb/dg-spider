# encoding: utf-8
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

import json,re

# author:robot-2233
ENGLISH_MONTH = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'}


class cfrSpiderSpider(BaseSpider):
    name = 'cfr'
    website_id = 722  # 前面会报挺多403，后面情况会好些，主要是翻页那里出的错，但是是可以翻页的
    language_id = 1866
    start_urls = ['https://www.cfr.org/views/ajax?view_name=topic_filters_cards&view_display_id=filters_block&view_args=338&view_path=%2Ftaxonomy%2Fterm%2F338&view_base_path=&view_dom_id=ae217e8ea88c0888d3ee03400edc4f0db739a2deeaeb88d6defdc0368f97e206&pager_element=0&_wrapper_format=html&topics=All&regions=All&type=All&page=0',
                  'https://www.cfr.org/views/ajax?view_name=topic_filters_cards&view_display_id=filters_block&view_args=339&view_path=%2Ftaxonomy%2Fterm%2F339&view_base_path=&view_dom_id=786bed3879340503a534bfbe1f72581888d6e7d8ddcd638ac188be5418ac288d&pager_element=0&_wrapper_format=html&topics=All&regions=All&type=All&page=0',
                  'https://www.cfr.org/views/ajax?view_name=topic_filters_cards&view_display_id=filters_block&view_args=340&view_path=%2Ftaxonomy%2Fterm%2F340&view_base_path=&view_dom_id=0f5d8c86a50a049128380b5025c97f3f43f76822979118cfd5c36c025ef88a72&pager_element=0&_wrapper_format=html&topics=All&regions=All&type=All&page=0',
                  'https://www.cfr.org/views/ajax?view_name=topic_filters_cards&view_display_id=filters_block&view_args=341&view_path=%2Ftaxonomy%2Fterm%2F341&view_base_path=&view_dom_id=9321c6317c3570b7e318392dc55ff4956e20aa4e7ffb7c2c60ee7c8cdaae06d3&pager_element=0&_wrapper_format=html&topics=All&regions=All&type=All&page=0',
                  'https://www.cfr.org/views/ajax?view_name=topic_filters_cards&view_display_id=filters_block&view_args=342&view_path=%2Ftaxonomy%2Fterm%2F342&view_base_path=&view_dom_id=d5f1991b771f95391a187212689bbb9034e5e68f1e24e8ba24386ca7eb2dd42e&pager_element=0&_wrapper_format=html&topics=All&regions=All&type=All&page=0',
                  'https://www.cfr.org/views/ajax?view_name=topic_filters_cards&view_display_id=filters_block&view_args=343&view_path=%2Ftaxonomy%2Fterm%2F343&view_base_path=&view_dom_id=b2e50c24b614be07a02bd349114b40d480e3f4a839836445e5ee3c2abd7fa90d&pager_element=0&_wrapper_format=html&topics=All&regions=All&type=All&page=0',
                  'https://www.cfr.org/views/ajax?view_name=topic_filters_cards&view_display_id=filters_block&view_args=344&view_path=%2Ftaxonomy%2Fterm%2F344&view_base_path=&view_dom_id=37297a9996cfa96d639051f109e2fd71ff915ee768eb4bd723090a33f219e412&pager_element=0&_wrapper_format=html&topics=All&regions=All&type=All&page=0',
                  'https://www.cfr.org/views/ajax?view_name=topic_filters_cards&view_display_id=filters_block&view_args=345&view_path=%2Ftaxonomy%2Fterm%2F345&view_base_path=&view_dom_id=8cc42663ba3b094bdb22d916a75cfaefc3ca5ca436cb9f72a7fd1a14df46febf&pager_element=0&_wrapper_format=html&topics=All&regions=All&type=All&page=0',]
    proxy = '02'

    def parse(self, response):
        aim_json=BeautifulSoup(response.text, 'html.parser').text
        if 'page=0' in response.url:
            aim_html=json.loads(aim_json)[1]['data']  # 离谱，但是确实是这样的
        else:
            aim_html=json.loads(aim_json)['1']['data']  # 离谱，但是确实是这样的
        soup=BeautifulSoup(aim_html,'html.parser')
        for i in soup.find_all(class_=re.compile('views-row krt-grid__list-item')):
            each_it=i.select_one(' .card-article-large__date').text.split(' ')
            time_=each_it[-1]+'-' + OldDateUtil.EN_1866_DATE[each_it[1]] + '-' + (each_it[2] if len(each_it[2])==3 else '0'+each_it[2]).strip(',') + ' 00:00:00'
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_,'category1_':aim_html.split('action="/')[1].split('" method')[0],'title_':i.select_one(' .card-article-large__title').text.strip()}
                url='https://www.cfr.org/'+i.select_one(' .card-article-large__link')['href'].strip()
                if 'video' not in url and 'event' not in url and 'timeline' not in url and 'podcasts' not in url:
                    yield Request(url, callback=self.parse_item, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request(response.url.split('page=')[0]+'page='+str(int(response.url.split('page=')[-1])+1))

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] =response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        try:
            item['body'] =soup.select_one(' .body-content').text
        except:
            item['body'] = soup.body.text[5500:-1000].strip('\n')
        item['abstract'] =soup.find(class_=re.compile('__description')).text
        item['pub_time'] = response.meta['pub_time_']
        try:
            item['images'] =soup.find(class_=re.compile('__figure')).img['src'].replace('//','https://')
        except:
            item['images'] =None
        yield item
