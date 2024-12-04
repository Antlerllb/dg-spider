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

class thaicnSpider(BaseSpider):  # author：田宇甲 遇到个没时间的网站，没写时间戳检查
    name = 'thaicn'
    website_id = 230
    language_id = 2266
    start_urls = ['http://www.thaicn.net/e/action/ListInfo/?classid=2']
    proxy = '02'
    is_http = 1

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .news_list table')[1].select('tr a')[0:11]:
            meta = {'category1_': i.text}
            yield Request(i['href']+'&page=0', callback=self.Mushroom, meta=meta)

    def Mushroom(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' body table:nth-child(10) td a')[3:59:2]:
            response.meta['title_'] = str(i).split('alt="')[1].split('"')[0]
            response.meta['images_'] = 'http://www.thaicn.net'+i.img['src']
            yield Request(i['href'], callback=self.parse_item, meta=response.meta)
        page = response.url.split('&page=')[1]
        yield Request(response.url.replace('page='+page, 'page='+str(int(page)+1)), callback=self.Mushroom, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        try:
            if 'gUT泰国华人中文网站【泰华网】' in soup.select('body table:nth-child(10) tr td.main table:nth-child(2) span')[-1]:
                body = soup.find_all(style="font-size: medium;")
                item['body'] = '\n'.join([i.text for i in body[0:len(body)-2]]).strip().strip(' ').strip()
                item['abstract'] = body[1].text.strip().strip(' ').strip()
            elif soup.select_one('#text') is not None:
                item['body'] = soup.select_one('#text').text.strip().strip(' ').strip()
                item['abstract'] = soup.select_one('#text').text.strip().strip(' ').strip()
            else:
                item['body'] = '\n'.join([i.text for i in soup.select('body table:nth-child(10) tr td.main table:nth-child(2) span')]).strip().strip(' ').strip()
                item['abstract'] = soup.select('body table:nth-child(10) tr td.main table:nth-child(2) span')[1].text.strip().strip(' ').strip()
        except:
            item['body'] = 'Page Not Found!'  # 有些链接指向一个空网页，什么都没有
            item['abstract'] = 'Page Not Found!'
        item['pub_time'] = OldDateUtil.get_now_datetime_str()
        item['images'] = response.meta['images_']
        yield item
