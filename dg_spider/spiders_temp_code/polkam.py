


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

#author:蔡卓妍
# check:why
#有status:403  网站直接有时候打开会522
def p_time(pt):
    ptime = pt.split(',')[1].split()
    if len(ptime[0]) < 2:
        ptime[0] = '0' + ptime[0]
    try:
        l_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + '00:00:00'
    except:
        l_time = datetime.datetime.strptime(pt.split(',')[1].strip(), '%d %B %Y')
    return l_time
class PolkamSpider(BaseSpider):
    name = 'polkam'
    website_id = 79
    language_id = 1952
    start_urls = ['https://polkam.go.id/berita/',
                  'https://polkam.go.id/berita-deputi/']
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        flag = True
        last_time = p_time(soup.select('article .text span')[-1].text.strip())
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
            category1 = response.url.split('/')[3].strip()
            lists = soup.select('article')
            for i in lists:
                news_url = i.select_one('.entire-meta-link')['href']
                title = i.select_one('.post-header a').text.strip()
                ptime = i.select_one('.text span').text.strip()
                pub_time = p_time(ptime)
                meta = {'pub_time': pub_time, 'title': title, 'category1': category1}
                yield Request(url=news_url, callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            p = response.url.split('/')[-2]
            if 'page/' not in response.url:
                next_page = response.url + 'page/2'
            else:
                next_page = response.url.replace(str(p), f"{str(int(p) + 1)}")
            yield Request(url=next_page, callback=self.parse)

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['pub_time'] = response.meta['pub_time']
        item['body'] = "\n".join(i.text.strip() for i in soup.select('p'))
        item['images'] = [i.get('src') for i in (soup.select('.post-featured-img img'))]
        item['abstract'] = soup.select_one('p').text.strip()
        yield item