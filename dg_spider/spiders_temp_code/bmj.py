


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy

# author:杨洛华
# check: pys pass
German_MONTH = {
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

class bmjSpider(BaseSpider):
    name = 'bmj'
    website_id = 1682
    language_id = 1898
    start_urls = ['https://www.bmj.de/SiteGlobals/Forms/Suche/Newsarchivsuche_Formular.html']
    proxy = '00'

    def parse(self, response):
        meta = response.meta
        articles = response.xpath(".//div[@class='small-12 columns']")
        for article in articles:
            try:
                ssd = article.xpath(".//h3[@class='seachresult teaser']/a/span/text()").get().strip("|").replace(".","").split(" ")
                time = "{}-{}-{}".format(ssd[2],German_MONTH[ssd[1]],ssd[0]) + " 00:00:00"
            except:
                continue
            title = article.xpath(".//h3[@class='seachresult teaser']/a/text()").extract()[1]
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time) >= int(OldDateUtil.time):
                meta['time'] = time
                meta['title'] = title
                yield Request(url='https://www.bmj.de/' + article.xpath(".//h3/a/@href").get(), callback=self.parse_item, meta=deepcopy(meta))
        if response.xpath(".//div[@class='navIndex']//a[@class='forward button ']/@href").get() is None:
            self.logger.info("到达最后一页")
        else:
            yield Request(url='https://www.bmj.de/' + response.xpath(".//div[@class='navIndex']//a[@class='forward button ']/@href").get(), callback=self.parse, meta=deepcopy(meta))

    def parse_item(self, response):
            item = NewsItem(language_id=self.language_id)
            item['category1'] = 'Suchergebnisse'
            item['category2'] = None
            item['title'] = response.meta['title']
            item['pub_time'] = response.meta['time']
            item['body'] = '\n'.join(response.xpath('//*[@id="content"]/p/text()').extract())
            item['images'] = ["https://www.bmj.de/" + i for i in response.xpath("//*[@id='content']/p[1]/span/img/@src").extract()]
            try:
                item['abstract'] = response.xpath("//*[@id='content']/div[1]/p/text()").get()
            except:
                item['abstract'] = item['body'].split('\n')[0]
            return item



