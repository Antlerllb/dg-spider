# encoding: utf-8



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy

# check:魏芃枫 pass
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
        'ต.ล.': '10',
        'พ.ย.': '11',
        'ธ.ค.': '12'}

class MofSpider(BaseSpider):
    name = 'mof'
    # allowed_domains = ['mof.go.th']
    start_urls = ['http://www.mof.go.th/th/thumbs/1543205599'] # 其他的模块大部分都是PDF，格式也比较乱，更像文件而非新闻
    website_id = 1607
    language_id = 2208

    def parse(self, response):
        t = response.xpath('//div[@class="all_thum"]//li//div[@class="date_detail"]/text()').getall()[-1].split(' ')
        last_time = str(int(t[2]) - 543) + "-" + Tai_MONTH[t[1]] + "-" + str(t[0]) + " 00:00:00"
        meta = {'pub_time_': last_time}
        for i in response.xpath('//div[@class="title_news"]/a'):
            # if 'pdf' in i.xpath('@href').getall()[0]:
            #     pass
            # else:
            yield Request(url=i.xpath('@href').getall()[0], callback=self.parse_pages, meta=meta)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            try:
                yield Request(url=response.xpath('//div[@class="pagination2f"]/ul//a[contains(@rel,"next")]/@href').getall()[0],
                              callback=self.parse, meta=deepcopy(meta))
            except AttributeError:
                pass


    def parse_pages(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.xpath('//div[@class="headline_insite"]/text()').getall()
        tt = response.xpath('//div[@class="box_view"]/text()').getall()[0].split(' ')
        time = str(int(tt[2]) - 543) + "-" + Tai_MONTH[tt[1]] + "-" + str(tt[0]) + " 00:00:00"
        item['pub_time'] = time
        item['images'] = response.xpath('//div[@class="row"]//img/@src').getall()
        item['body'] = ''.join(response.xpath('//div[@class="content-fullpage2f"]/p/text()').getall())
        item['category1'] = "ข่าวกระทรวงการคลัง"
        item['abstract'] = None
        item['category2'] = "ภาพข่าวและกิจกรรม"
        yield item




