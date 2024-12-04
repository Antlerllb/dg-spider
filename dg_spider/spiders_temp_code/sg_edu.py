# encoding: utf-8
import json
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


# Author:陈卓玮
# check：凌敏 pass
class edu_sg_spider(BaseSpider):
    name,website_id,language_id,params_news_rows,start_urls = 'edusg',434,1866,1,[f'https://search.moe.gov.sg/solr/moe_search_index/select?q=*&app=site_search&fq=content_type_s%3A(%22news%22)&fq=active_b:true&rows=1&start=0&sort=modified_dt%20desc']
    def parse(self,response):
        if len(json.loads(response.text)['response']['docs']) == 1:yield Request(f"https://search.moe.gov.sg/solr/moe_search_index/select?q=*&app=site_search&fq=content_type_s%3A(%22news%22)&fq=active_b:true&rows={int(json.loads(response.text)['response']['numFound'])}&start=0&sort=modified_dt%20desc")
        else:
            for i in json.loads(response.text)['response']['docs']:
                if OldDateUtil.time == None or OldDateUtil.str_datetime_to_timestamp(i['end_dt'].replace("T", " ").replace("Z", "")) >= OldDateUtil.time:yield Request(url ="https://www.moe.gov.sg" + i['link_s'], callback=self.parse_essay, meta={'title':i['name_s'], 'category1':i['news_category_s'], 'pub_time':i['end_dt'].replace("T", " ").replace("Z", ""), 'abstract':BeautifulSoup(i['_content_ngram'], 'lxml').text})
    def parse_essay(self,response):
        soup,item = BeautifulSoup(response.text,'lxml'),NewsItem()
        item['title'],item['category1'],item['body'],item['abstract'],item['pub_time'],item['images'] = response.meta['title'],response.meta['category1'],'\n'.join((i.text.replace('\n','') for i in soup.select('p'))),response.meta['abstract'],response.meta['pub_time'],list(k.get('src') for k in soup.select('img'))
        yield item
