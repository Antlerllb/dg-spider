


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy

# author:杨洛华
# check: pys pass
class BmfsfjSpider(BaseSpider):
    name = 'bmfsfj'
    website_id = 1686
    language_id = 1898
    start_urls = ['https://www.bmfsfj.de/bmfsfj/aktuelles/alle-meldungen/72630!search?state=H4sIAAAAAAAAADXMsQ7CMAwE0F9BN2coa9aizh34AatxIVKIwXYGqPrvBBDbvTvpNiRynlRuiLWVEr4-y18rLeyGuO0B1-w2s850YcTjEPBorE9EIOCV76Mk_sFEvafP0yGxLb1qxqfOUaq5Uq59X6kY728cLL0JgQAAAA%3D%3D&pageNum=0']
    proxy = '00'

    def parse(self, response):
        meta = response.meta
        flag = True
        articles = response.xpath(".//div[@class='search-wrapper']/ul/li")
        for article in articles:
            article_url = article.xpath(".//div[@class='teaser-wrapper']//@href").get()
            title = article.xpath(".//div[@class='teaser-wrapper'][1]//a/text()").get()
            abstract = article.xpath(".//div[@class='teaser-wrapper'][2]/p/text()").get()
            meta['title'] = title
            meta['abstract'] = abstract
            yield Request(url='https://www.bmfsfj.de/' + article_url, callback=self.parse_item, meta=deepcopy(meta))
        if flag:
            num = int(response.xpath(".//li[@class='pager-item next']//@value").get()) + 1
            try:
                next_page = 'https://www.bmfsfj.de/bmfsfj/aktuelles/alle-meldungen/72630!search?state=H4sIAAAAAAAAADXMsQ7CMAwE0F9BN2coa9aizh34AatxIVKIwXYGqPrvBBDbvTvpNiRynlRuiLWVEr4-y18rLeyGuO0B1-w2s850YcTjEPBorE9EIOCV76Mk_sFEvafP0yGxLb1qxqfOUaq5Uq59X6kY728cLL0JgQAAAA%3D%3D&pageNum=' + str(num)
            except:
                next_page = None
            yield Request(url=next_page, callback=self.parse, meta=deepcopy(meta))

    def parse_item(self,response):
        meta = response.meta
        ssd = response.xpath(".//time/@datetime").get().split("T")[0].split("-")
        pub_time = "{}-{}-{}".format(ssd[0], ssd[1], ssd[2]) + " 00:00:00"
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1'] = 'Alle Meldungen'
            item['category2'] = None
            item['title'] = meta['title']
            item['abstract'] = meta['abstract']
            item['pub_time'] = pub_time
            item['body'] ='\n'.join(response.xpath('//*[@id="article"]/div[2]/p/text()').extract())
            item['images'] = ['https://www.bmfsfj.de' + i for i in response.xpath("//*[@id='article']//img/@src").extract()]
            return item

