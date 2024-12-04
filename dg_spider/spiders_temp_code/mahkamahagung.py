# -- coding: utf-8 --**


import json
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
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
from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
Month = {'Januari': '01',
         'Februari': '02',
         'Maret': '03',
         'April': "04",
         'Mei': '05',
        'Juni': '06',
        'Juli': '07',
        'Agustus': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Desember': '12'} # 印尼语月份

#author: 蔡卓妍
def p_time(pt):
    ptime = pt.split(',')[1].strip().split()
    if len(ptime[0]) < 2:
        ptime[0] = '0' + ptime[0]
    l_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + ptime[3] + ':00'
    return l_time
class MahkamahagungSpider(BaseSpider):
    name = 'mahkamahagung'
    website_id = 120
    language_id = 1952
    start_urls = ['https://www.mahkamahagung.go.id/id/berita',
                  'https://www.mahkamahagung.go.id/id/pengumuman',
                  'https://www.mahkamahagung.go.id/id/keputusan',
                  'https://www.mahkamahagung.go.id/id/artikel']
    proxy = '02'
    data1 = {'cat_id': '1','page': '1','lang': 'id'}
    data2 = {'cat_id': '2', 'page': '1', 'lang': 'id'}
    data7 = {'cat_id': '7', 'page': '1', 'lang': 'id'}
    data3 = {'cat_id': '3', 'page': '1', 'lang': 'id'}

    def start_requests(self): # post请求
        for url in self.start_urls:
            if 'berita' in url:
                yield scrapy.FormRequest(url=url, callback=self.parse, dont_filter=True, formdata=self.data1)
            elif 'pengumuman' in url:
                yield scrapy.FormRequest(url=url, callback=self.parse, dont_filter=True, formdata=self.data2)
            elif 'artikel' in url:
                yield scrapy.FormRequest(url=url, callback=self.parse, dont_filter=True, formdata=self.data3)
            elif 'keputusan' in url:
                yield scrapy.FormRequest(url=url, callback=self.parse, dont_filter=True, formdata=self.data7)

    def parse(self, response):
        soup = json.loads(response.text)['data']['rows']
        flag = True
        try:
            last_time = p_time(soup[-1]['pt'])
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
                for i in soup:
                    title = i['title']
                    category1 = i['cat']
                    news_url = i['url']
                    pub_time = p_time(i['pt'])
                    yield Request(url=news_url, callback=self.parse_item, meta={'pub_time':pub_time, 'category1':category1, 'title':title})
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:
                    if 'berita' in response.url:
                        self.data1['page'] = str(int(self.data1['page']) + 1)
                        yield scrapy.FormRequest(url=response.url,callback=self.parse,dont_filter=True,formdata=self.data1)
                    elif 'pengumuman' in response.url:
                        self.data2['page'] = str(int(self.data2['page']) + 1)
                        yield scrapy.FormRequest(url=response.url,callback=self.parse,dont_filter=True,formdata=self.data2)
                    elif 'artikel' in response.url:
                        self.data3['page'] = str(int(self.data3['page']) + 1)
                        yield scrapy.FormRequest(url=response.url,callback=self.parse,dont_filter=True,formdata=self.data3)
                    elif 'keputusan' in response.url:
                        self.data7['page'] = str(int(self.data7['page']) + 1)
                        yield scrapy.FormRequest(url=response.url,callback=self.parse,dont_filter=True,formdata=self.data7)
        except:
            self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text,'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        if soup.select('p')[1:-1] != []:
            item['body'] = '\n'.join(i.text.strip() for i in soup.select('p')[1:-1])
            if soup.select('p')[1].text.strip() == '':
                item['abstract'] = soup.select('p')[2].text.strip()
            else:
                item['abstract'] = soup.select('p')[1].text.strip()
        else:
            item['body'] = '\n'.join(i.text.strip() for i in soup.select('h1')[:-7])
            item['abstract'] = soup.select_one('h1').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [i['src'] for i in soup.select('img')[2:-3]]
        yield item