


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


class ProthomaloSpider(BaseSpider):
    name = 'prothomalo'
    website_id = 2276
    language_id = 1779
    author = '王晋麟'

    bn_ct = ['politics', 'bangladesh', 'world-rest15', 'business', 'opinion-rest15',
             'sports-all', 'entertainment-rest15', 'chakri-all', 'lifestyle-rest15']
    ct2 = ['রাজনীতি', 'বাংলাদেশ', 'বিশ্ব', 'বাণিজ্য', 'মতামত', 'খেলা', 'বিনোদন', 'চাকরি',
           'জীবনযাপন']
    en_ct = ['bangladesh', 'international', 'opinion', 'business', 'youth', 'entertainment', 'lifestyle']
    req_url = ['https://www.prothomalo.com/api/v1/collections/{}?offset={}&limit=10',
               'https://en.prothomalo.com/api/v1/collections/{}?offset={}&limit=10']
    lan_id = [1779, 1866]

    def start_requests(self):
        for j in [0, 1]:
            if j == 0:
                yield Request(url=self.req_url[j].format(self.bn_ct[0], 10), callback=self.parse,
                              meta={'category1': self.ct2[0], 'offset': 10, 'ind': 0, 'lan': j})
            else:
                yield Request(url=self.req_url[j].format(self.en_ct[0], 10), callback=self.parse,
                              meta={'category1': self.en_ct[0], 'offset': 10, 'ind': 0, 'lan': j})

    def parse(self, response):
        js = response.json()
        flag = True
        if len(js['items']) != 0:
            for item in js['items']:
                news_pubtime_stamp = str(item['story']['last-published-at'])[0:10]
                news_pubtime = OldDateUtil.timestamp_to_datetime_str(news_pubtime_stamp)
                if OldDateUtil.time is None or int(OldDateUtil.time + 1800) <= OldDateUtil.str_datetime_to_timestamp(news_pubtime):
                    news_url = item['story']['url']
                    news_title = item['story']['headline']
                    news_abstract = item['story']['summary']
                    yield Request(url=news_url, callback=self.parse_item,
                                  meta={'title': news_title, 'abstract': news_abstract,
                                        'category1': response.meta['category1'], 'pub_time': news_pubtime,
                                        'lan': response.meta['lan']})
                else:
                    flag = False
                    break
            if flag:
                ind = response.meta['ind']
                offset = response.meta['offset'] + 10
                if response.meta['lan'] == 0:
                    yield Request(url=self.req_url[0].format(self.bn_ct[ind], offset), callback=self.parse,
                                  meta={'category1': self.ct2[ind], 'offset': offset, 'ind': ind, 'lan': 0})
                elif response.meta['lan'] == 1:
                    yield Request(url=self.req_url[1].format(self.en_ct[ind], offset), callback=self.parse,
                                  meta={'category1': self.en_ct[ind], 'offset': offset, 'ind': ind, 'lan': 1})
            else:
                ind = response.meta['ind'] + 1
                if response.meta['lan'] == 0 and ind < len(self.bn_ct):
                    yield Request(url=self.req_url[0].format(self.bn_ct[ind], 10), callback=self.parse,
                                  meta={'category1': self.ct2[ind], 'offset': 10, 'ind': ind, 'lan': 0})
                elif response.meta['lan'] == 1 and ind < len(self.en_ct):
                    yield Request(url=self.req_url[1].format(self.en_ct[ind], 10), callback=self.parse,
                                  meta={'category1': self.en_ct[ind], 'offset': 10, 'ind': ind, 'lan': 1})
        else:
            ind = response.meta['ind'] + 1
            if response.meta['lan'] == 0 and ind < len(self.bn_ct):
                yield Request(url=self.req_url[0].format(self.bn_ct[ind], 10), callback=self.parse,
                              meta={'category1': self.ct2[ind], 'offset': 10, 'ind': ind, 'lan': 0})
            elif response.meta['lan'] == 1 and ind < len(self.en_ct):
                yield Request(url=self.req_url[1].format(self.en_ct[ind], 10), callback=self.parse,
                              meta={'category1': self.en_ct[ind], 'offset': 10, 'ind': ind, 'lan': 1})

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['body'] = '\n'.join(
            [content.text.replace('\\u200', '').strip() for content in soup.select('.story-element-text p') if
             content.text.strip() != ''])
        if item['body'] != '':
            item['category1'] = response.meta['category1'].strip()
            item['title'] = ' '.join(response.meta['title'].strip().split())
            item['pub_time'] = response.meta['pub_time']
            item['language_id'] = self.lan_id[response.meta['lan']]
            item['images'] = []
            item['abstract'] = ' '.join(response.meta['abstract'].strip().split()) if response.meta['abstract'] is not None else item['body'].split('\n')[0].strip()
            if len(item['body'].split('\n')) == 1:
                item['body'] = item['abstract'].strip() + '\n' + item['body'].strip()
            yield item
