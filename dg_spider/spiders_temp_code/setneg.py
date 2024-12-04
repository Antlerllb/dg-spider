


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
class SetnegSpider(BaseSpider):
    name = 'setneg'
    website_id = 76
    language_id = 1952
    start_urls = ['https://www.setneg.go.id/listcontent/listberita/berita_foto',
                  'https://www.setneg.go.id/listcontent/listberita/berita_kemensetneg',
                  "https://www.setneg.go.id/listcontent/listberita/berita_presiden_dan_pemerintah",
                  'https://www.setneg.go.id/listcontent/listberita/pidato_presiden',
                  'https://www.setneg.go.id/listcontent/listberita/berita_wakil_presiden',
                  'https://www.setneg.go.id/listcontent/listberita/artikel',
                  'https://www.setneg.go.id/listcontent/listberita/serba_serbi',
                  'https://www.setneg.go.id/listcontent/listberita/siaran_pers_kemensetneg',
                  'https://www.setneg.go.id/listcontent/listberita/infografis']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        ltime = soup.select('.col-sm-8.no-padder .media')[-1].select_one('.media-body p').text.split(',')[1].split()
        last_time = ltime[2] + '-' + Month[ltime[1]] + '-' + ltime[0] + ' ' + '00:00:00'
        category1 = soup.select_one('.page.animsition > div > div.row > div > div > div > h2').text.strip()
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
            lists = soup.select('.col-sm-8.no-padder .media')
            for i in lists:
                title = i.select_one('.media-body h4 a').text
                ptime = i.select_one('.media-body p').text.split(',')[1].split()
                pub_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + '00:00:00'
                news_url = 'https://www.setneg.go.id' + i.select_one('.media-body h4 a').get('href')
                meta = {'pub_time': pub_time, 'title': title, 'category1': category1}
                yield Request(url=news_url, callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = 'https://www.setneg.go.id' + soup.select('.pagination.pagination-no-border >li > a')[-2].get("href")
            yield Request(url=next_page, callback=self.parse)

    def parse_item(self,response): #有一些是图片集的新闻 所以body空
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        try:
            item['body'] = "\n".join(i.text.strip() for i in soup.select('.padding-top-10.col-content.my-content-text > p'))
            if soup.select_one('.padding-top-10.col-content.my-content-text > p').text.strip() == '':
                item['abstract'] = soup.select('.padding-top-10.col-content.my-content-text > p')[1].text.strip()
            else:
                item['abstract'] = soup.select_one('.padding-top-10.col-content.my-content-text > p').text.strip()
        except:
            item['body'] = "\n".join(i.text.strip() for i in soup.select('span'))
            if soup.select_one('span').text.strip() == '':
                item['abstract'] = soup.select('span')[1].text.strip()
            else:
                item['abstract'] = soup.select_one('span').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [i.get("src") for i in soup.select(".col-sm-8.no-padder .outer-fiture-foto img")]
        yield item
