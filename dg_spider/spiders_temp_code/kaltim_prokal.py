


from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
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
#有小小部分会报status:403
class Kaltim_prokalSpider(BaseSpider):
    name = 'kaltim_prokal'
    website_id = 49
    language_id = 1952
    start_urls = ['https://kaltim.prokal.co/rubrik/index/15-utama.html',
                  'https://kaltim.prokal.co/rubrik/index/18-balikpapan.html',
                  'https://kaltim.prokal.co/rubrik/index/21-samarinda.html',
                  'https://kaltim.prokal.co/rubrik/index/27-pro-bisnis.html',
                  'https://kaltim.prokal.co/rubrik/index/36-kaltim.html',
                  'https://kaltim.prokal.co/rubrik/index/40-olahraga.html',
                  'https://kaltim.prokal.co/rubrik/index/43-hiburan.html',
                  'https://kaltim.prokal.co/rubrik/index/60-lifestyle.html',
                  'https://kaltim.prokal.co/rubrik/index/33-nasional.html']
    proxy = '02'

    def parse(self, response): #除url外 内容全部从具体新闻中获取
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        ltime = soup.select('.media-body small')[-1].text.split(",")[-1].strip().split()
        last_time = ltime[2] + '-' + Month[ltime[1]] + '-' + ltime[0] + ' ' + ltime[3] + ':00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
            category1 = soup.select_one('.text-primary').text
            lists = [soup.select_one('.content-artikel a')] + soup.select('.media-body a')
            for i in lists:
                news_url = i.get('href')
                yield Request(url=news_url, callback=self.parse_item, meta={'category1':category1},dont_filter=True)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = soup.find(rel="next").get('href')
            yield Request(url=next_page, callback=self.parse)

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text,'html.parser')
        item['title'] = soup.select_one('.content-artikel-judul').text
        item['category1'] = response.meta['category1']
        item['body'] = "\n".join(i.text.strip() for i in soup.select('p'))
        if soup.select_one('p').text.strip() == '':
            item['abstract'] = soup.select('p')[1].text.strip()
        else:
            item['abstract'] = soup.select_one('p').text.strip()
        ptime = soup.select_one('.content-artikel-tanggal').text.split(",")[-1].strip().split()
        item['pub_time'] = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + ptime[3] + ':00'
        item['images'] = [i.select_one('img').get('src') for i in soup.find_all(clas="content-artikel-image")]
        yield item