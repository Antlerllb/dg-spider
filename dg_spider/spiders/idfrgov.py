

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
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil as mutong


class idfrgovSpider(BaseSpider):#文章没有时间 不写时间截止
    name = 'idfrgov'
    website_id = 422
    language_id = 2036
    start_urls = ['https://www.idfr.gov.my/ms/berita-terkini']


#aurhor：李沐潼
    # check: wpf pass
    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}
        meta['category1']=soup.select('.content-category>h1')[0].text
        url = soup.select('.list-title>a')
        for u in url:
            yield Request('https://www.idfr.gov.my'+u.get('href'),meta=meta,callback=self.parse_items)
        next_url=soup.select('.next')
        if next_url==[]:
            pass
        elif len(next_url)==1:
            nu=next_url[0].get('href')
            yield Request('https://www.idfr.gov.my'+nu,meta=meta,callback=self.parse)
        else:
            nu = next_url[1].get('href')
            yield Request('https://www.idfr.gov.my' + nu, meta=meta, callback=self.parse)
    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        body=soup.select('article>p')
        item = NewsItem(language_id=self.language_id)

        item['title'] = soup.select('.uk-article-title')[0].text

        item['category1'] = response.meta['category1']
        item['category2'] = None
        b = []
        for i in body:
            if i.select('em') == []:
                b.append(i.text)
            else:
                b.append(''.join([j.text for j in i.select('em')]))
        item['body']=''.join(b)

        if body[1].text ==None:
            item['abstract'] = item['body']
        else:
            item['abstract'] = body[1].text
        item['pub_time'] = OldDateUtil.get_now_datetime_str()#这个网站news没有日期，用当前时间代替
        img=soup.select('article>p>img')
        a=[]
        if img != []:
            for i in img:
                a.append('https://www.idfr.gov.my/' + i.get('src'))
        item['images'] =a





        yield item


