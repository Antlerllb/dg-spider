


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy

# author:杨洛华
# check: pys pass
class BmwkSpider(BaseSpider):
    name = 'bmwk'
    website_id = 1681
    language_id = 1898
    start_urls = ["https://www.bmwk.de/SiteGlobals/BMWI/Forms/Listen/Medienraum/Medienraum_Formular.html?resourceId=184318&input_=184194&pageLocale=de&templateQueryStringListen=&to=&from=&documentType_=PressRelease&documentType_.GROUP=1&cl2Categories_LeadKeyword=&cl2Categories_LeadKeyword.GROUP=1&selectSort=&selectSort.GROUP=1&selectTimePeriod=&selectTimePeriod.GROUP=1#form-184318"]

    def parse(self, response):
        meta = response.meta
        articles = response.xpath("//*[@id='main']/div[4]/ul/li")
        for article in articles:
            ssd = article.xpath(".//div[@class='card-block']/p[@class='card-topline']/span/text()").get().split(".")
            time = "{}-{}-{}".format(ssd[2],ssd[1],ssd[0]) + " 00:00:00"
            title = article.xpath(".//div[@class='card-block']/p[2]/strong/text()").get()
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time) >= int(OldDateUtil.time):
                meta['time'] = time
                meta['title'] = title
                yield Request(url="https://www.bmwk.de/" + article.xpath(".//div/div[@class='card-block']/a/@href").get(), callback=self.parse_item, meta=deepcopy(meta))
        if response.xpath("//*[@id='main']/div[6]/ul/li[4]/a/@href").get() is None:
            self.logger.info("到达最后一页")
        else:
            yield Request(url="https://www.bmwk.de/" + response.xpath("//*[@id='main']/div[6]/ul/li[4]/a/@href").get(), callback=self.parse, meta=deepcopy(meta))

    def parse_item(self, response):
            item = NewsItem(language_id=self.language_id)
            item['category1'] ='Pressemitteilung'
            item['category2'] = None
            item['title'] = response.meta['title']
            item['body'] = '\n'.join(response.xpath("//*[@id='main']/div[2]/div/div/div/p/text()").extract())
            item['abstract'] = item['body'].split('\n')[0]
            item['pub_time'] = response.meta['time']
            item['images'] = ["https://www.bmwk.de" + i for i in response.xpath("//*[@id='main']//picture/img/@src").extract()]
            return item

