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
class mypaperSpider(BaseSpider):#数据量很少
    i=1
    name = 'mypaper'
    website_id = 202
    language_id = 2266
    start_urls = ['https://www.mypaper.sg']
    # proxy = '02'
#check: wpf pass
#aurhor：李沐潼

    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}

        meta['category1']='News'
        news_url_li = soup.select('.text-center>a')
        for i in news_url_li:
            new_url = i.get('href')
            yield Request(new_url,meta=meta,callback=self.parse_items)

        try:
            next_url = soup.select('.next')[0].get('href')
            yield Request(next_url,meta=meta,callback=self.parse)
        except:
            pass




    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        ti=soup.select('.entry-date')[0].text.strip()
        ti_li=ti.split(', ')
        if len(ti_li[0].split(' ')[1])==1:
            pub_time="{}-{}-0{} 00:00:00".format(ti_li[1],e_month[ti_li[0].split(' ')[0]],ti_li[0].split(' ')[1])
        else:

            pub_time="{}-{}-{} 00:00:00".format(ti_li[1],e_month[ti_li[0].split(' ')[0]],ti_li[0].split(' ')[1])



        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1']=response.meta['category1']
            item['category2'] = None
            item['pub_time']=pub_time

            title=soup.select('.entry-title')[0].text
            item['title']=title

            body_li = soup.select('.entry-content')
            body = ''.join([i.text.strip() for i in body_li])
            item['body']=body

            abstract = body_li[0].select('p')[1].text
            item['abstract']=abstract

            image_li = soup.select('.featured-thumbnail img')
            images = []
            if image_li != []:
                for image in image_li:
                    images.append(image.get('src'))
            else:
                pass
            item['images']=images

            yield item




