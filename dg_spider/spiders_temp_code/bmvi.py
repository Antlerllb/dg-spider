


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy

# author:杨洛华
# check：pys
# pass
class BmviSpider(BaseSpider):
    name = 'bmvi'
    website_id = 1688
    language_id = 1898
    start_urls = ["https://www.bmvi.de/SiteGlobals/Forms/Listen/DE/BMVI-Aktuell/BMVI-Aktuell_Formular.html?input_=212876&submit=Ergebnisse+filtern&resourceId=14470&selectSort=commonSortDate_dt+desc&selectSort.GROUP=2&documentType_=PressRelease&documentType_.GROUP=1&cl2Categories_Themen.GROUP=1&pageLocale=de"]

    def parse(self, response):
        meta = response.meta
        articles = response.xpath(".//ul[@class='card-list']/li/div")
        for article in articles:
            ssd = article.xpath("./div/p[2]/text()[2]").get().split(".")
            time = "{}-{}-{}".format(ssd[2],ssd[1],ssd[0]).replace(" ", '') + " 00:00:00"
            title = article.xpath("./p[2]/a//text()").get()
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time) >= int(OldDateUtil.time):
                meta['time'] = time
                meta['title'] = title
                yield Request(url="https://www.bmvi.de/" + article.xpath("./p[2]/a/@href").get(), callback=self.parse_item, meta=deepcopy(meta))
        if response.xpath("//*[@id='main']/div[4]/ul/li[4]/a/@href").get() is None:
            self.logger.info("到达最后一页")
        else:
            yield Request(url="https://www.bmvi.de/" + response.xpath("//*[@id='main']/div[4]/ul/li[4]/a/@href").get(), callback=self.parse, meta=deepcopy(meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['category1'] = 'Pressemitteilung'
        item['category2'] = None
        item['title'] = response.meta['title']
        item['body'] = '\n'.join(response.xpath(".//div[@class='content']/div/p//text()").extract())
        item['abstract'] = item['body'].split('\n')[0]
        item['pub_time'] = response.meta['time']
        item['images'] = ["https://www.bmvi.de" + i for i in response.xpath(".//div[@class='content']//img/@src").extract()]
        return item
