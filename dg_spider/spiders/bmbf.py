


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
class BmbfSpider(BaseSpider):
    name = 'bmbf'
    website_id = 1690
    language_id = 1898
    start_urls = ["https://www.bmbf.de/SiteGlobals/Forms/bmbf/suche/pressemitteilungen/Pressemitteilungensuche_Formular.html"]

    def parse(self, response):
        meta = response.meta
        articles = response.xpath(".//section[@class='l-teaser-list']/a")
        for article in articles:
            ssd = article.xpath("./div[1]/h2/small/span[1]/time/text()").get().split(".")
            time = "{}-{}-{}".format(ssd[2],ssd[1],ssd[0].strip('\n').strip(' ')) + " 00:00:00"
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time) >= int(OldDateUtil.time):
                meta['time'] = time
                yield Request(url="https://www.bmbf.de/" + article.xpath("./@href").get(), callback=self.parse_item, meta=deepcopy(meta))
        try:
            num = int(response.xpath(".//ul[@class='c-nav-index__list']/li[5]/a/text()").get())
            for i in range(2,num+1):
                yield Request(url='https://www.bmbf.de/SiteGlobals/Forms/bmbf/suche/pressemitteilungen/Pressemitteilungensuche_Formular.html?gtp=33424_list%253D' + str(i), callback=self.parse, meta=deepcopy(meta))
        except:
            pass


    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['category1'] = 'Pressemitteilung'
        item['category2'] = None
        item['title'] = ''.join(response.xpath(".//h1[@class='c-intro__headline  ']/span[1]//text()").extract())
        item['body'] = '\n'.join(response.xpath(".//div[@class='s-richtext js-richtext']/p//text()").extract())
        item['abstract'] = ''.join(response.xpath(".//div[@class='c-intro__introduction']/p//text()").extract())
        item['pub_time'] = response.meta['time']
        if response.xpath(".//span[@class='c-picture__wrapper']/img/@src").get() is None:
            item['images'] = None
        else:
            if 'static1' in response.xpath(".//span[@class='c-picture__wrapper']/img/@src").get():
                item['images'] = ['' + i for i in response.xpath(".//span[@class='c-picture__wrapper']/img/@src").extract()]
            else:
                item['images'] = ['https://www.bmbf.de' + i for i in response.xpath(".//span[@class='c-picture__wrapper']/img/@src").extract()]
        return item

