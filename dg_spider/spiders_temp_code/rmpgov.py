


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
import scrapy
import requests


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
headers = {
         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
 }



class rmpgovSpider(BaseSpider):#有的新闻图片占位但是都不显示，没有爬这些图片，只爬了看得见的图片，且这些图片的url非常长。
    name = 'rmpgov'             #有的新闻url看起来有点怪，不是全部标亮那种，但是全部复制浏览器打开是正常新闻
    website_id = 418
    language_id = 2036
    start_urls = ['https://www.rmp.gov.my/arkib-berita/berita/page/1']
    j = 1

#aurhor：李沐潼
# check: wpf pass
    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}
        meta['category1']=soup.select('.sfContentBlock>h2')[-1].text
        news_url_li1 = soup.select('.sfnewsTitle>a')
        ti = soup.select('.sfnewsMetaInfo')

        for k in range(len(ti)):
            ti_li = ti[k].text.strip().split(', ')
            meta['pub_time'] = self.pub_time="{}-{}-{} 00:00:00".format(ti_li[1], e_month_sim[ti_li[0].split(' ')[0]], ti_li[0].split(' ')[1])

            yield Request('https://www.rmp.gov.my/arkib-berita/berita/' + news_url_li1[k].get('href')[3:],meta=meta,callback=self.parse_items)




        while True:
            rmpgovSpider.j = rmpgovSpider.j + 1
            try_url = self.start_urls[0][:48] + str(rmpgovSpider.j)
            try_res = requests.get(try_url, headers=headers)
            ll = mutong(try_res.text, 'html.parser')
            if ll.select('.sf_PagerPrevGroup') == []:
                yield Request(try_url,meta=meta,callback=self.parse)
            else:
                if ll.select('.sf_PagerPrevGroup')[0].text == '...' and rmpgovSpider.j>675:
                    break



    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(self.pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1']=response.meta['category1']
            item['category2'] = None
            item['pub_time']=response.meta['pub_time']

            title = soup.select('.sfnewsTitle')[0].text.strip()
            item['title']=title

            body_li = soup.find_all(dir="auto")
            if body_li != []:
                body = ''.join(i.text.strip() for i in body_li)
            else:
                body_li = soup.select('p')
                body = ''.join(i.text.strip() for i in body_li)
            item['body']=body

            try:
                abstract = body_li[0].text.strip()
            except:
                abstract = None
            item['abstract']=abstract

            images=[]
            image = soup.select('.sfnewsContent>img')
            for i in image:
                if i.get('src')[:4] == 'data':
                    images.append(i.get('src'))
            if images!=[]:
                item['images']=images
            else:
                item['images']=None



            yield item


