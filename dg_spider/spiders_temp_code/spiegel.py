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


German_month = {
    'Januar': '01',
    'Februar': '02',
    'März': '03',
    'April': '04',
    'Mai': '05',
    'Juni': '06',
    'Juli': '07',
    'August': '08',
    'September': '09',
    'Oktober': '10',
    'November': '11',
    'Dezember': '12'
}
# check:wpf pass
class SpiegelSpider(BaseSpider): # author:田宇甲
    name = 'spiegel'   # 跑不出来可能是网络问题！记得代理什么的换换 
    website_id = 1763
    language_id = 1898
    start_urls = [f'https://www.spiegel.de/{i}/' for i in ['thema/ukraine_konflikt', 'plus', 'thema/coronavirus', 'thema/klimawandel', 'ausland', 'panorama', 'sport', 'wirtschaft']]
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .z-10.w-full article'):  # 第一页会有排版的问题，网站会有一些新闻不给出时间然后报list index out of range这是正常的，不影响爬虫，后面就不会报错了
            try:
                ssd = i.select_one(' footer span').text.split(', ')[0].split(' ')
                time_ = ssd[-1] + '-' + German_month[ssd[1]] + '-' + (ssd[0].strip('.') if int(ssd[0].strip('.')) > 9 else '0'+ssd[0].strip('.')) + ' 00:00:00'
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    meta = {'pub_time_': time_, 'category1_': response.url.split('de/')[1].split('/')[0], 'title_': i.select_one(' .w-full').text.strip(), 'abstract_': i.select_one(' .mb-12').text.strip(), 'images_': i.picture.img['src']}
                    yield Request(i.select_one(' .w-full a')['href'], callback=self.parse_item, meta=meta)
            except:
                pass
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            if 'plus' in response.url or 'panorama' in response.url:
                if response.url.count('p') < 4:
                    yield Request(response.url+'p2/')
                else:
                    yield Request(response.url.split('/p')[0]+'/p'+response.url.split('/p')[1]+'/p'+str(int(response.url.split('/p')[-1].strip('/'))+1)+'/')
            else:
                if 'p' not in response.url:
                    yield Request(response.url+'p2/')
                else:
                    yield Request(response.url.split('/p')[0]+'/p'+str(int(response.url.split('/p')[1].strip('/'))+1)+'/')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        try:
            item['body'] = soup.select_one(' .lg:mt-32.md:mt-32.sm:mt-24.md:mb-48.lg:mb-48.sm:mb-32').text
        except:
            item['body'] = soup.body.text[5500:-1000].strip('\n')
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
