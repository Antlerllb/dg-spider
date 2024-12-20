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

class publicoSpider(BaseSpider):
    name = 'publico'
    website_id = 2073
    language_id = 2122
    start_urls = ['https://www.publico.pt/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.select('#masthead-container > div.masthead__menus > nav.masthead__nav.masthead__nav--tags > ul li a'):
            url = i.get('href')
            category1 = i.text
            if 'https' not in url:
                url = 'https://www.publico.pt' + url
            meta = {'category1':category1}
            yield Request(url = url,meta=meta,callback=self.essay_list_parser)

    def essay_list_parser(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        meta = response.meta
        try_next_page=False
        for i in soup.select('#ul-listing > li'):
            essay_url = i.select_one('a').get('href')
            essay_time = i.select_one('time').get('datetime').split(', ')[1].strip(' GMT') #day month year datetime
            essay_time = essay_time.split(' ')[2] + "-" +"""{:0>2d}""".format(str(OldDateUtil.EN_1866_DATE[essay_time.split(' ')[1]]).zfill(2)) + "-" + essay_time.split(' ')[0] + " " + essay_time.split(' ')[3]
            essay_time_stamp = OldDateUtil.str_datetime_to_timestamp(essay_time)
            if OldDateUtil.time==None or int(essay_time_stamp) >= OldDateUtil.time:
                try_next_page=True  #时间截止-翻页->同一页可能会有比截止时间更早的新闻

            meta.update({'time':essay_time})
            yield Request(url = essay_url,meta=meta,callback=self.essay_parser)

        if try_next_page:
            try:
                next_page_url = response.url.split('=')[0]+'='+str(int(response.url.split('=')[-1])+1)
            except:
                next_page_url = response.url +"?page=2"
            meta.update({'time':None})
            # print("翻页中--"+next_page_url)
            yield Request(url = next_page_url,meta=meta,callback=self.essay_list_parser)

    def essay_parser(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            category2 = soup.select_one('.story__labels a').text
        except:
            category2=''
        title = soup.select_one('h1').text.strip()
        content = ''
        for i in soup.select('p'):
            content += i.text + '\n'
        img = []
        for i in soup.select('img'):
            if 'http' in i.get('src'):
                img.append(i.get('src'))

        item = NewsItem(language_id=self.language_id)
        item['title'] = title
        item['category1'] = response.meta['category1']
        item['category2'] = category2
        item['body'] = content
        item['abstract'] = content.split('\n')[0]
        item['pub_time'] = response.meta['time']
        item['images'] = img
        yield item

