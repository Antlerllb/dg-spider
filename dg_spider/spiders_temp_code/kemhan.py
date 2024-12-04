


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
import datetime
Month = {'Januari': '01',
         'Februari': '02',
         'Maret': '03',
         'April': "04",
         'Mei': '05',
        'Juni': '06',
        'Juli': '07',
        'Agustus': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Desember': '12'} # 印尼语月份

#author: 蔡卓妍
def p_time(pt):
    ptime = pt.split(',')[1].split()
    if len(ptime[0]) < 2:
        ptime[0] = '0' + ptime[0]
    try:
        l_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + '00:00:00'
    except:
        l_time = datetime.datetime.strptime(pt.split(',')[1].strip(), '%d %B %Y')
    return l_time
class KemhanSpider(BaseSpider):
    name = 'kemhan'
    website_id = 88
    language_id = 1952
    start_urls = ['https://www.kemhan.go.id/category/berita', 'https://www.kemhan.go.id/setjen/category/berita',
                  'https://www.kemhan.go.id/itjen/category/berita', 'https://www.kemhan.go.id/renhan/category/berita',
                  'https://www.kemhan.go.id/ropeg/category/berita', 'https://www.kemhan.go.id/pusrehab/category/berita',
                  'https://www.kemhan.go.id/pothan/category/berita', 'https://www.kemhan.go.id/kuathan/category/berita',
                  'https://www.kemhan.go.id/baranahan/category/berita', 'https://www.kemhan.go.id/balitbang/category/berita',
                  'https://www.kemhan.go.id/rohumas/category/berita', 'https://www.kemhan.go.id/puslapbinkuhan/category/berita',
                  'https://www.kemhan.go.id/pusdatin/category/berita', 'https://www.kemhan.go.id/puslaik/category/berita',
                  'https://www.kemhan.go.id/badiklat/category/berita', 'https://www.kemhan.go.id/strahan/category/berita',
                  'https://www.kemhan.go.id/bainstrahan/category/berita']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        last_time = p_time(soup.select('.listing-news small')[-1].text.strip())
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
            lists = soup.select('.listing-news')
            ca = response.url.split('/')[3].strip()
            if ca == 'category':
                category1 = 'berita'
            else:
                category1 = ca
            for i in lists:
                title = i.select_one('h4 a').text
                pub_time = p_time(i.select_one('small').text.strip())
                news_url = i.select_one('h4 a').get("href")
                meta = {'pub_time': pub_time, 'title': title, 'category1': category1}
                yield Request(url=news_url, callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = soup.select('.paging li a')[-2].get('href')
            yield Request(url=next_page, callback=self.parse)

    def parse_item(self,response): #有一些是图片集新闻，body为空
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text,'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = 'berita'
        item['body'] = '\n'.join(i.text.strip() for i in soup.select(".bg-w .article p"))
        try:
            a = soup.select_one(".bg-w .article p").text.strip()
            for i in soup.select(".bg-w .article p"):
                if i.text.strip() != '':
                    item['abstract'] = i.text.strip()
                    break
                else:
                    item['abstract'] = ''
            item['pub_time'] = response.meta['pub_time']
            item['images'] = [i.get('src') for i in soup.select('p img')] #有一些图片是data:image
            yield item
        except: #内容是空的(图片也没有
            pass
