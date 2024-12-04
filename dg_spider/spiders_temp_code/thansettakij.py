# encoding: utf-8



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil



#   Author:叶雨婷
Tai_MONTH = {
        'ม.ค.': '01',
        'ก.พ.': '02',
        'มี.ค': '03',
        'เม.ย.': '04',
        'พ.ค.': '05',
        'มิ.ย.': '06',
        'ก.ค.': '07',
        'ส.ค.': '08',
        'ก.ย': '09',
        'ก.ย.': '09',
        'ต.ล.': '10',
        'พ.ย.': '11',
        'ธ.ค.': '12'}

class ThansettakijSpider(BaseSpider):
    name = 'thansettakij'
    index = 1
    start_urls = ['https://www.thansettakij.com/category/']
    website_id = 1581
    language_id = 2208

    def parse(self, response):
        list_pages = ["business","property","money_market","economy","columnist","politics","Motor","world"]
        for item in list_pages:
            meta_part = {'e': item}
            # print("https://www.thansettakij.com/category/" + item)
            i = "?page={}".format(self.index)
            yield Request(url="https://www.thansettakij.com/category/" + item + i, callback=self.get_page, meta=meta_part)

    def get_page(self, response):
        last_time = response.xpath('//div[@class="news-content"]/p/text()').getall()
        if last_time == []:
            pass
        else:
            t = last_time[-1].split(' ')
            last_time = str(int(t[2]) - 543) + "-" + Tai_MONTH[t[1]] + "-" + str(t[0]) + " 00:00:00"
            for i in response.xpath('//div[@class="container"]//a/@href').getall()[::2]:
                meta = {'href': i}
                yield Request(url='https://www.thansettakij.com' + i, callback=self.parse_pages, meta=meta)
                # 又是动态的，这里去掉了category就可以直接进入网页的doc的response
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            try:
                item = response.meta['e']
                self.index = self.index + 1
                i = "?page={}".format(self.index)
                # 动态网站，自动加载新的新闻，这个是抓包的url的那啥
                # 这里翻页403会有点多，后面会好些
                yield Request(url="https://www.thansettakij.com/category/" + item + i, callback=self.parse)
            except AttributeError:
                pass


    def parse_pages(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.xpath('//div[@class="page-title-content mt-4"]/h1/text()').getall()
        if title != []:
            item['title'] = title
            t = response.xpath('//div[@class="info"]/span/text()').getall()[3].split(' ')
            last_time = str(int(t[2]) - 543) + "-" + Tai_MONTH[t[1]] + "-" + str(t[0]) + " 00:00:00"
            item['pub_time'] = last_time
            item['images'] = response.xpath('//img/@src').getall()[2:]
            item['body'] = ''.join(response.xpath('//div[contains(@class,"content-detail")]//p/text()').getall())
            try:
                item['category1'] = response.meta['href'].split('/')[1]
            except:
                item['category1'] = None
            item['abstract'] = None
            item['category2'] = None
            yield item
        else:
            pass




