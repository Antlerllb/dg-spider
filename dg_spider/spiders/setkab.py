


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
class SetkabSpider(BaseSpider):
    name = 'setkab'
    website_id = 113
    language_id = 1952
    start_urls = ['https://setkab.go.id/category/transkrip-pidato/',
                  'https://setkab.go.id/category/berita/',
                  'https://setkab.go.id/category/artikel/',
                  'https://setkab.go.id/category/peraturan/',
                  'https://setkab.go.id/category/nusantara/',
                  'https://setkab.go.id/category/dwp/',
                  'https://setkab.go.id/category/pengumuman/'] #除前两个外，其余更新较慢

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        flag = True
        ptime = soup.select('.card_search .text .date')[-1].text.strip().split()
        if len(ptime[0]) < 2:
            ptime[0] = '0' + ptime[0]
        last_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + '00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
            category1 = soup.select_one('.title_page .title').text
            lists = soup.select(".card_search")
            for i in lists:
                title = i.select_one('.text h2').text
                article = i.select_one('a').get("href")
                ptime = i.select_one('.text .date').text.strip().split()
                if len(ptime[0]) < 2:
                    ptime[0] = '0' + ptime[0]
                pub_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + '00:00:00'
                meta = {'pub_time': pub_time, 'title': title,'category1': category1}
                yield Request(url=article, callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = soup.select_one('a.next.page-numbers').get("href")
            yield Request(url=next_page, callback=self.parse)

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text,'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['body'] = "\n".join(i.text.strip() for i in soup.select('.reading_text p'))
        item['abstract'] = soup.select_one('.reading_text p').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [i.get('src') for i in soup.select('.reading_text img')]
        yield item
