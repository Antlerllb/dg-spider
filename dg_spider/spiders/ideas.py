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

headers = {
         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
 }
class ideasSpider(BaseSpider):#所有新闻都没有图片 没有爬图片
    i=1
    name = 'ideas'
    website_id = 711
    language_id = 2037
    start_urls = ['https://www.ideas.org.my/news-opinion/?tx_category=news&_page=1']
    proxy = '02'

# check: wpf pass
#aurhor：李沐潼

    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}

        category1_li = soup.select('.column_attr>h1')[0].text.strip()
        meta['category1']=category1_li
        category2_li = soup.select('select>option')[1].text
        meta['category2']=category2_li

        news_url_li1 = soup.select('.pt-cv-title>a')

        for k in news_url_li1:
            yield Request(k.get('href'),meta=meta,callback=self.parse_items)

        while True:
            ideasSpider.i=ideasSpider.i+1
            next_url=self.start_urls[0][:62]+str(ideasSpider.i)
            response = requests.get(next_url,headers=headers, verify=False)
            so = mutong(response.text, 'html.parser')
            if 'No posts found.' not in so.text:
                yield Request(next_url,meta=meta,callback=self.parse)
            else:
                break





    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        t = soup.select('.entry-date')[0].get('datetime')
        t_li = t.split('T')
        pub_time = '{} 00:00:00'.format(t_li[0])



        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1']=response.meta['category1']
            item['category2'] = response.meta['category2']
            item['pub_time']=pub_time

            title = soup.select('.entry-title')[0].text.strip()
            item['title']=title

            body_li = soup.select('p')
            body = ''.join(i.text.strip() for i in body_li)
            item['body']=body


            abstract = body_li[0].text.strip()
            item['abstract']=abstract

            image = soup.select('.image_wrapper>img')
            if image!=[]:
                item['images']=image[0].get('src')
            else:
                item['images'] =None

            yield item




