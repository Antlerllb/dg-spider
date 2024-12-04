# encoding: utf-8
import html
import json

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



#注：HEADER中要增加
#'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnQiOiJhd2FuaV93ZWIiLCJkZXZpY2VJZCI6Ijk4M2M0MjZkLTM3YzktNGNjMS1iN2FiLWU0YWYxOTQxZmRkZiIsImlhdCI6MTY1NjU3MjY4NSwiZXhwIjoxNjU3MTc3NDg1fQ.xly-Cqqqnp2U9qKmbdLKJ0FjIWmR7wWXUqHuJ2pFO8I'
#才可正常访问


# Author:陈卓玮
# check：凌敏 pass
class astroawanispider(BaseSpider):
    name = 'astroawani'
    website_id = 387
    language_id = 2036

    pageNumber=1
    api = f'https://de-api.eco.astro.com.my/combineFeed/api/v2?pageSize=50&pageNumber={pageNumber}&language=bm&site=awani'
    start_urls = [api]

    Headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnQiOiJhd2FuaV93ZWIiLCJkZXZpY2VJZCI6Ijk4M2M0MjZkLTM3YzktNGNjMS1iN2FiLWU0YWYxOTQxZmRkZiIsImlhdCI6MTY1NjU3MjY4NSwiZXhwIjoxNjU3MTc3NDg1fQ.xly-Cqqqnp2U9qKmbdLKJ0FjIWmR7wWXUqHuJ2pFO8I'
    }

    def parse(self, response):###获取文章列表数据
        data = json.loads(response.text)
        for i in data['response']:
            if i['type'] != 'VIDEO':
                essay_id = i['id']
                essay_api = f"https://de-api.eco.astro.com.my/feed/api/v1/articles/{essay_id}?site=awani"
                yield Request(url = essay_api,callback=self.essay_parser,headers=self.Headers)

        essay_publish_date_stamp = OldDateUtil.str_datetime_to_timestamp(data['response'][0]['publishDate'].split('T')[0] + " 00:00:00")

        if len(data)!=0 and (OldDateUtil.time == None or essay_publish_date_stamp >= OldDateUtil.time):
            pageNumber = 1
            try:
                if response.meta['pageNumber']<101:
                    pageNumber = response.meta['pageNumber']+1
            except:
                pass
            api = f'https://de-api.eco.astro.com.my/combineFeed/api/v2?pageSize=50&pageNumber={pageNumber}&language=bm&site=awani'
            # print(api)
            yield Request(url = api,meta={'pageNumber':pageNumber},headers=self.Headers)


    def essay_parser(self,response):
        data = json.loads(response.text)
        img=[]
        img.append(data['response']['imageUrl'])
        item = NewsItem(language_id=self.language_id)
        item['title'] = data['response']['title']
        item['category1'] = data['response']['primaryCategorySlug']
        item['body'] = BeautifulSoup(html.unescape(data['response']['articleBody']), 'lxml').text
        item['abstract'] = data['response']['description']
        item['pub_time'] = data['response']['publishDate'].split('T')[0]+" 00:00:00"
        item['images'] = img
        yield item