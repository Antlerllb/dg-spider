# encoding: utf-8
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
        'Nopember': '11',
        'Desember': '12'} # 印尼语月份

#author: 蔡卓妍
#body空的是纯图片
def p_time(pt):
    ptime = pt.split(',')[1].split()
    if len(ptime[0]) < 2:
        ptime[0] = '0' + ptime[0]
    l_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + '00:00:00'
    return l_time
class KomnashamSpider(BaseSpider):
    name = 'komnasham'
    website_id = 123
    language_id = 1952
    start_urls = ['https://www.komnasham.go.id/index.php/news/',
                  'https://www.komnasham.go.id/index.php/agenda/',
                  'https://www.komnasham.go.id/index.php/pengkajian-penelitian/',
                  'https://www.komnasham.go.id/index.php/pendidikan-penyuluhan/',
                  'https://www.komnasham.go.id/index.php/pemantauan-penyelidikan/',
                  'https://www.komnasham.go.id/index.php/mediasi/',
                  'https://www.komnasham.go.id/index.php/penanganan-pelanggaran-berat-ham/',
                  'https://www.komnasham.go.id/index.php/pelayanan-pengaduan/',
                  'https://www.komnasham.go.id/index.php/penanganan-konflik/',
                  'https://www.komnasham.go.id/index.php/pengawasan/',
                  'https://www.komnasham.go.id/index.php/kantor-perwakilan/',
                  'https://www.komnasham.go.id/index.php/rekam-media/'] #除第一个外 其余更新慢

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        last_time = p_time(soup.select('.post-content')[-1].select_one('.post-meta').text)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
            category1 = soup.select_one('.block-title').text
            lists = soup.select('.post-content')
            for i in lists:
                news_url = 'https://www.komnasham.go.id' + i.select_one('h3 a')['href']
                title = i.select_one('h3 a').text
                pub_time = p_time(i.select_one('.post-meta').text)
                meta = {'pub_time':pub_time, 'title':title, 'category1':category1}
                yield Request(url=news_url, callback=self.parse_item,meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            try: #有一些新闻极少 没有翻页
                next_page = 'https://www.komnasham.go.id' + soup.select('.pagination li')[-1].select_one('a')['href']
                yield Request(url=next_page, callback=self.parse)
            except:
                self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text,'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['pub_time'] = response.meta['pub_time']
        try:
            item['body'] = ''.join(i.text.replace('\xa0','\n') for i in soup.select('.entry-content div'))
            if soup.select_one('.entry-content div').text.strip() == '':
                item['abstract'] = soup.select('.entry-content div')[1].text.strip()
            else:
                item['abstract'] = soup.select_one('.entry-content div').text.strip()
        except:
            try:
                item['body'] = '\n'.join(i.text.replace('\r\n',' ').strip() for i in soup.select('.entry-content p'))
                if soup.select_one('.entry-content p').text.strip() == '':
                    item['abstract'] = soup.select('.entry-content p')[1].text.replace('\r\n',' ').strip()
                else:
                    item['abstract'] = soup.select_one('.entry-content p').text.replace('\r\n',' ').strip()
            except:
                item['body'] = '\n'.join(i.text.strip() for i in soup.select('.entry-content'))
                item['abstract'] = soup.select_one('.entry-content').text.strip()
        try:
            item['images'] = [i['src'] for i in soup.select('.entry-content p img')] + [soup.select_one('.single-post img')['src']]
        except:
            try:
                item['images'] = [soup.select_one('.single-post img')['src']]
            except:
                item['images'] = []
        yield item
