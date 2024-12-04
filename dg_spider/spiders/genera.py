import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil





Spanish_2181_DATE = {'enero': '01',
                       'febrero': '02',
                       'marzo': '03',
                       'abril': '04',
                       'mayo': '05',
                       'junio': '06',
                       'julio': '07',
                       'agosto': '08',
                       'septiembre': '09',
                       'octubre': '10',
                       'noviembre': '11',
                       'diciembre': '12'}

#author:林泽佳
# check:czy
class GeneraSpider(BaseSpider):
    name = 'genera'
    website_id = 2133  # 网站的id(必填)
    language_id = 2181  # 所用语言的id
    # allowed_domains = ['generaccion.com']
    start_urls = ['http://www.generaccion.com']
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2"}
    is_http = 1
    # proxy = "02"

    def parse(self, response):
        lis1 = ["editorial", "actualidad", "deportes", "espectaculos", "salud", "ecologia", "inmuebles",
               "emprendedores"]
        url1 = [f'http://www.generaccion.com/{type}/archivo/' for type in lis1]
        for i in url1:#直接进入解析标签
            yield Request(url=i, callback=self.parse2, headers={'Referer': 'http://www.generaccion.com'})

    def parse2(self, response):#无二级标签的解析对所有标签进行解析
        articles = response.xpath("//div[@class='idt']/h2/a/@href").extract()
        if len(articles) !=0:#如果不为空，则说明标签页有新闻，进入解析页面
            for i in articles:
                    yield Request(url=i, callback=self.parse4, headers={'Referer': 'http://www.generaccion.com'})
            url = response.xpath("//a[@class='navprv']/@href").extract_first()
            yield Request(url=url, callback=self.parse2)  # 遍历完之后也进入前一天
        else:
            url = response.xpath("//a[@class='navprv']/@href").extract_first()
            yield Request(url=url,callback=self.parse2)  # 如果没有就进入前一天

    def parse4(self, response):

        tm = response.xpath("//div[@class='gro mod']/text()").extract_first()
        time_list = tm.split(' ')#Jueves 06 de octubre 2022

        time1 = "{}-{}-{} {}:{}:{}".format(time_list[4], Spanish_2181_DATE[time_list[3]], time_list[1],
                                           "00","00","00")# c

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time1) >= OldDateUtil.time:
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.xpath("//div[@class='cen']/h1/text()").extract()[0].strip()

            cate_list = response.xpath("//div[@class='man']/div/text()").extract_first()
            catas = cate_list.split(' ')#MÁS NOTICIAS DE Actualidad
            cata1 = catas[3]

            item['category1'] = cata1#response.xpath("//span[class='uppercase primary-color bold h6 ']/a/text()").extract()[0]
            item['category2'] = ''

            body1 = "".join(response.xpath("//div[@class='crp']").xpath('string(.)').extract())
            remove = re.compile(r'\r\n', re.S)
            body = re.sub(remove, '', body1)
            item['body'] = body

            item['abstract'] = response.xpath("//div[@class='gro mod']/text()").extract()[1].strip()
            item['pub_time'] = time1
            item['images'] = response.xpath("//div[@id='img']//img/@src").extract()
            yield item
        else:
            self.logger.info("时间截止")
