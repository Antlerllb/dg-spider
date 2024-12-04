


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
 }

categorys= {'SINGAPORE':'https://www.asiaone.com/jsonapi/node/article?page%5Boffset%5D=0&'
                        'page%5Blimit%5D=12&fields%5Bnode--article%5D=title%2Ccreated%2Cfield_source%2Cfield_rotator_headline%2Cfield_category%'
                        '2Cfield_image%2Cpath%2Cdrupal_internal__nid&fields%5Bfile--file%5D=image_style_uri&fields%5Btaxonomy_term--source%'
                        '5D=name&fields%5Btaxonomy_term--category%5D=name&include=field_source%'
                        '2Cfield_image%2Cfield_category&sort=-field_publication_date&filter%5Bcategory%5D%5Bcondition%5D%5Bpath%5D=field_category.drupal_internal__tid&'
                        'filter%5Bcategory%5D%5Bcondition%5D%5Bvalue%5D=2&'
                        'filter%5Bstatus%5D%5Bcondition%5D%5Bpath%5D=status&filter%5Bstatus%5D%5Bcondition%5D%5Bvalue%5D=1',
            'MALAYSIA':'http://www.asiaone.com/jsonapi/node/article?page%5Boffset%5D=0&page%5Blimit%5D=12&fields%5Bnode--article%5D=title%'
                       '2Ccreated%2Cfield_source%2Cfield_rotator_headline%2Cfield_category%2Cfield_image%2Cpath%2Cdrupal_internal__nid&fields%5Bfile--file%5D=image_style_uri&'
                       'fields%5Btaxonomy_term--source%5D=name&fields%5Btaxonomy_term--category%5D=name&include=field_source%2Cfield_image%2Cfield_category&sort=-field_publication_date&filter%'
                       '5Bcategory%5D%5Bcondition%5D%5Bpath%5D=field_category.drupal_internal__tid&filter%5Bcategory%5D%5Bcondition%5D%5Bvalue%5D=3&filter%'
                       '5Bstatus%5D%5Bcondition%5D%5Bpath%5D=status&filter%5Bstatus%5D%5Bcondition%5D%5Bvalue%5D=1',
           'CHINA':'http://www.asiaone.com/jsonapi/node/article?page%5Boffset%5D=0&page%5Blimit%5D=12&fields%5Bnode--article%5D=title%2Ccreated%2Cfield_source%'
                   '2Cfield_rotator_headline%2Cfield_category%2Cfield_image%2Cpath%2Cdrupal_internal__nid&fields%5Bfile--file%5D=image_style_uri&fields%5Btaxonomy_term--source%5D=name&fields%'
                   '5Btaxonomy_term--category%5D=name&include=field_source%2Cfield_image%2Cfield_category&sort=-field_publication_date&filter%5Bcategory%5D%5Bcondition%5D%5Bpath%5D=field_category.drupal_internal__tid&'
                   'filter%5Bcategory%5D%5Bcondition%5D%5Bvalue%5D=63335&'
                   'filter%5Bstatus%5D%5Bcondition%5D%5Bpath%5D=status&filter%5Bstatus%5D%5Bcondition%5D%5Bvalue%5D=1',
           'ASIA':'http://www.asiaone.com/jsonapi/node/article?page%5Boffset%5D=0&page%5Blimit%5D=12&fields%5Bnode--article%5D=title%2Ccreated%2Cfield_source%2Cfield_rotator_headline%2Cfield_category%'
                  '2Cfield_image%2Cpath%2Cdrupal_internal__nid&fields%5Bfile--file%5D=image_style_uri&fields%5Btaxonomy_term--source%5D=name&fields%5Btaxonomy_term--category%5D=name&include=field_source%'
                  '2Cfield_image%2Cfield_category&sort=-field_publication_date&filter%5Bcategory%5D%5Bcondition%5D%5Bpath%5D=field_category.drupal_internal__tid&filter%5Bcategory%5D%5Bcondition%5D%5Bvalue%5D=4&filter%'
                  '5Bstatus%5D%5Bcondition%5D%5Bpath%5D=status&filter%5Bstatus%5D%5Bcondition%5D%5Bvalue%5D=1',
           'WORLD':'http://www.asiaone.com/jsonapi/node/article?page%5Boffset%5D=0&page%5Blimit%5D=12&fields%5Bnode--article%5D=title%2Ccreated%2Cfield_source%2Cfield_rotator_headline%2Cfield_category%'
                   '2Cfield_image%2Cpath%2Cdrupal_internal__nid&fields%5Bfile--file%5D=image_style_uri&fields%5Btaxonomy_term--source%5D=name&fields%5Btaxonomy_term--category%5D=name&include=field_source%'
                   '2Cfield_image%2Cfield_category&sort=-field_publication_date&filter%5Bcategory%5D%5Bcondition%5D%5Bpath%5D=field_category.drupal_internal__tid&filter%5Bcategory%5D%5Bcondition%5D%5Bvalue%5D=5&filter%'
                   '5Bstatus%5D%5Bcondition%5D%5Bpath%5D=status&filter%5Bstatus%5D%5Bcondition%5D%5Bvalue%5D=1'}

class asiaoneSpider(BaseSpider):#所有新闻都没有图片 没有爬图片
    name = 'asiaone'
    website_id = 437
    language_id = 1866
    start_urls = ['https://www.asiaone.com/']
    proxy = '02'

#aurhor：李沐潼

    def parse(self, response):
        meta = {}
        meta['category1'] = 'News'
        for i in categorys:
            meta['category2'] = i
            yield Request(categorys[i],meta=meta,callback=self.parse_page)


    def parse_page(self,response):
        js = json.loads(response.text)
        new_url_li = js['data']
        for i in new_url_li:
            new_url = i['links']['self']['href']
            yield Request(new_url,meta=response.meta,callback=self.parse_items)

        next_url = js['links']['next']['href']
        try:
            yield Request(next_url,meta=response.meta,callback=self.parse_page)
        except:
            pass

    def parse_items(self,response):
        js = json.loads(response.text)
        pub_time_try = js['data']['attributes']['revision_timestamp']
        pub_time = '{} 00:00:00'.format(pub_time_try.split('T')[0])
        # print(pub_time)


        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1']=response.meta['category1']
            item['category2'] = response.meta['category2']
            item['pub_time']=pub_time

            title = js['data']['attributes']['title']
            item['title']=title

            body_str = js['data']['attributes']['body']['value']
            body_li = mutong(body_str, 'html.parser')

            body = ''.join(i.text.strip() for i in body_li)
            item['body']=body
            flag=True
            for i in body_li:
                if flag:
                    item['abstract'] = i.text
                    flag=False
                else:
                    break



            images = []
            img = body_li.select('img')
            if img!=[]:
                for i in img:
                    images.append('https://www.asiaone.com' + i.get('src'))
            else:
                try:
                    body_str = js['data']['relationships']['field_image']['links']['related']['href']
                    response_js = requests.get(body_str, headers=headers, verify=False)
                    body_str_js = json.loads(response_js.text)
                    body = [i for i in body_str_js['data']['attributes']['image_style_uri'][0].values()]
                    images = body
                except:
                    pass

            item['images']=images

            yield item


