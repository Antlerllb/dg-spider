from scrapy import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil



from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil as mutong
import scrapy
import requests
import json

headers = {
         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
# 'Connection':'close'


 }

category1={
'World':'https://www.todayonline.com/world',
    'Singapore':'https://www.todayonline.com/singapore'

}
e_month={
        'January':'01',
        'February':'02',
        'March':'03',
        'April':'04',
        'May':'05',
        'June':'06',
        'July':'07',
        'August':'08',
        'September':'09',
        'October':'10',
        'November':'11',
        'December':'12'
}
li=[]
urls={
    'Singapore':'https://www.todayonline.com/api/v1/infinitelisting/82413e48-6df8-4dfd-9362-e8985be2ddc0?_format=json&viewMode=infinite_scroll_listing_tdy&page=',
    'World':'https://www.todayonline.com/api/v1/infinitelisting/b7e8818d-c2f7-46f4-b8d6-f89d527898e5?_format=json&viewMode=infinite_scroll_listing_tdy&page='
}
class TodayonlineSpider(BaseSpider):
    name = 'todayonline'
    website_id = 206
    language_id = 1866
    start_urls = ['https://www.todayonline.com']
    proxy = '02'
    i=0
    j=0

#author：李沐潼

    def parse(self, response):
        meta={}
        for i in category1:
            meta['category1']=i
            if i == 'Singapore':
                while True:
                    next_url = urls['Singapore'] + str(TodayonlineSpider.i)
                    response_try = requests.get(next_url, timeout=10, headers=headers, verify=False)
                    TodayonlineSpider.i = TodayonlineSpider.i + 1
                    if response_try.status_code != 200:
                        break
                    else:
                        yield Request(next_url, meta=meta, callback=self.parse_page)
            if i=='World':
                while True:
                    next_url = urls['World'] + str(TodayonlineSpider.j)
                    response_try = requests.get(next_url, timeout=10, headers=headers, verify=False)
                    TodayonlineSpider.j = TodayonlineSpider.j + 1
                    if response_try.status_code != 200:
                        break
                    else:
                        yield Request(next_url, meta=meta, callback=self.parse_page)


    def parse_page(self,response):

        js = json.loads(response.text)
        for i in js['result']:
            new_url = i['absolute_url']
            yield Request(new_url, meta=response.meta, callback=self.parse_items)


    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        ti = soup.select('.article__row')[0].text
        ti_li = ti.split(' ')
        if len(ti_li[2][:-1]) == 1:
            pub_time = "{}-{}-0{} 00:00:00".format(ti_li[3], e_month[ti_li[1]], ti_li[2][:-1])
        else:
            pub_time = "{}-{}-{} 00:00:00".format(ti_li[3], e_month[ti_li[1]], ti_li[2][:-1])

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1']=response.meta['category1']
            item['category2'] = None
            item['pub_time']=pub_time


            title=soup.select('.h1--page-title')[0].text.strip()
            item['title']=title

            body_li = soup.select('.text-long')
            body = ''.join(i.text.strip() for i in body_li)
            item['body']=body
            if body_li[0]==None or len(body_li[0])<10:
                abstract=body
            else:
                abstract=body_li[0].text.strip()
            item['abstract']=abstract

            images = []
            image = soup.select('.image__wrapper>.image>img')
            for i in image:
                images.append(i.get('src'))
            item['images']=images

            yield item


