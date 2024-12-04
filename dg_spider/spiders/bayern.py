


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

deyu_month={
        'Januar':'01',
        'Februar':'02',
        'März':'03',
        'April':'04',
        'Mai':'05',
        'Juni':'06',
        'Juli':'07',
        'August':'08',
        'September':'09',
        'Oktober':'10',
        'November':'11',
        'Dezember':'12'
}
headers = {
         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
 }

cookie = {
    'LB_STK_BAYERN_DE': '962439946.20480.0000',
    'PHPSESSID': '1nqm6pev4184aqqkldpl7heq0f'
}

class bayernSpider(BaseSpider):#所有新闻都没有图片 没有爬图片
    name = 'bayern'
    website_id = 1697
    language_id = 1898
    start_urls = ['https://www.bayern.de/presse/pressemitteilungen/']

#aurhor：李沐潼
#check:wpf pass

    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}

        category1_li = soup.select('.breadcrumb-link')[-2].text
        meta['category1']=category1_li
        category2_li = soup.select('.section-form-filter>h1')[0].text
        meta['category2']=category2_li


        i = 1
        uuu = 'https://www.bayern.de/wp-content/themes/bayernde/functions.ajax.php'
        while True:
            data = {

                'action': 'byde_load_data',
                'kategorien': '[4,5,6,7,8,9,10,11,12,13,19,14,15]',

                'seitenid': '2453',
                'anzeige_3_spalte': 'ja',
                'inhalt_3_spalte': 'cat',
                'pagi': f'{i}'
            }
            i = i + 1
            response = requests.post(uuu, headers=headers, verify=False, data=data, cookies=cookie)
            so = mutong(response.text, 'html.parser')
            new_url_li = so.select('a')

            if new_url_li != []:
                for j in new_url_li:
                    new_url = j.get('href')
                    yield Request('https://www.bayern.de' + new_url,meta=meta,callback=self.parse_items)
            else:
                break



    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        tii = soup.select('.date-press-releases')[0].text.strip()

        tii_li = tii.split('. ')
        if len(tii_li[0]) == 1:
            pub_time = "{}-{}-0{} 00:00:00".format(tii_li[1].split(' ')[1], deyu_month[tii_li[1].split(' ')[0]],
                                                   tii_li[0])
        else:
            pub_time = "{}-{}-{} 00:00:00".format(tii_li[1].split(' ')[1], deyu_month[tii_li[1].split(' ')[0]],
                                                  tii_li[0])


        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1']=response.meta['category1']
            item['category2'] = response.meta['category2']
            item['pub_time']=pub_time

            title = soup.select('.sub-title')[0].text.strip()
            item['title']=title

            body_li = soup.select('.content-blocktext>p')
            body = ''.join(i.text.strip() for i in body_li)
            item['body']=body

            if body_li[0]==None or len(body_li[0])<10:
                abstract=body
            else:
                abstract = body_li[0].text.strip()
            item['abstract']=abstract
            item['images']=None

            yield item


