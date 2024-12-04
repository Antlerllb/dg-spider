

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


e_month_sim={
        'Jan':'01',
        'Feb':'02',
        'Mar':'03',
        'Apr':'04',
        'May':'05',
        'Jun':'06',
        'Jul':'07',
        'Aug':'08',
        'Sept':'09',
        'Sep':'09',
        'Oct':'10',
        'Nov':'11',
        'Dec':'12'
}
class sgcarmartSpider(BaseSpider):#最近新闻容易报403
    name = 'sgcarmart'
    website_id = 454
    language_id = 1866
    start_urls = ['https://www.sgcarmart.com/news/listing.php?CT=News']


#aurhor：李沐潼
# check: wpf pass
    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}
        meta['category1']=soup.select('.uniqueSetting>a')[0].text

        news_url_li1 = soup.find_all(id="rightside_content")

        for i in news_url_li1:
            news_url_li2 = i.select('.floatleft>a')
            for j in news_url_li2:
                if j.get('href')[0] == 'a':
                    yield Request('https://www.sgcarmart.com/news/' + j.get('href'),meta=meta,callback=self.parse_items)

        next_url_li = soup.select('.navigation_build>.pagebar')
        for i in next_url_li:
            if i.text == 'Next »':
                try:
                    yield Request('https://www.sgcarmart.com' + i.get('href'),meta=meta,callback=self.parse)
                except:
                    pass
                break

    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        tii = soup.find_all(id="rightside_content")
        ti = ''
        for i in tii:
            ti = i.select('.label')[0].text.strip()
        ti_li = ti.split(' ')
        pub_time = "{}-{}-{} 00:00:00".format(ti_li[2], e_month_sim[ti_li[1]], ti_li[0])

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)

            item['pub_time']=pub_time

            body_li = soup.find_all(align="left")
            if body_li != []:
                body = ''.join(i.text.strip() for i in body_li)
            else:
                body_li = soup.find_all(id="main_content")
                body = ''.join(i.text.strip() for i in body_li)
            item['body']=body

            try:
                abstract = body_li[0].text.strip()
            except:
                abstract = None
            item['abstract']=abstract


            item['title'] = soup.select('.uniqueSetting>a')[0].text.strip()

            item['category1'] = response.meta['category1']
            item['category2'] = None

            image_li = []
            images = []
            for i in body_li:
                image = i.select('a')
                if image != []:
                    image_li = image
                else:
                    image_li = soup.select('.fotorama__thumb>img')

            for image in image_li:
                try:
                    images.append(image.select('img')[0].get('src'))
                except:
                    images.append('https://www.sgcarmart.com' + image.get('href')[2:])
            item['images']=images


            yield item
        else:
            return


