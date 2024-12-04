


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from copy import deepcopy

# author:杨洛华
# check：pys
# pass
German_MONTH = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
}
class GtaiSpider(BaseSpider):
    name = 'gtai'
    website_id = 1729
    language_id = 1866
    start_urls = ['https://www.gtai.de/en/meta/search/66080!search;eNqVksFOwzAMht_F5yKtCAmp54kXgBvi4KbeyJQ6xU4GZdq7z90EhyGEuVnW99v5f-cAGwxUFLoD9FUjk-oNCuHSUEoUCg3QPUPkPWmBlwboIyTrWBV4Bx0gz3BsQGovMVzJfuJcUzI65MpFZi-uRmRRL57w3T15ohAxeXEKmfP4D59VSx7dD99ERg4kXn56RSV_5uNkx3qw6AcsMbPb9J64PM0T-c8lka5NQ3vb3t2v4HdV7XcGu7PKMmL5O9rLB13Cwi09xk9z0a4aeLsMsrVZbCdYJLQmDdCcy2Us8fAFCfKWvhUFF8n5HccT1ocWbA?page=0']

    def parse(self, response):
        meta = response.meta
        articles = response.xpath(".//div[@class='searchResults color-alternate']/ul/li")
        for article in articles:
            ssd = article.xpath("./div[1]/div[1]/span[1]/text()").get().replace(',','').split(' ')
            time = "{}-{}-{}".format(ssd[2],German_MONTH[ssd[0].strip()],ssd[1]) + " 00:00:00"
            title = article.xpath("./div[2]/a/h3/text()").get()
            abstract = article.xpath("./div[2]/p/text()").get()
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time) >= int(OldDateUtil.time):
                meta['time'] = time
                meta['title'] = title
                meta['abstract'] = abstract
                yield Request(url = 'https://www.gtai.de' + article.xpath("./div[2]/a/@href").get(), callback=self.parse_item, meta=deepcopy(meta))
        try:
            num = int(response.xpath(".//div[@class='searchOptions bottom light-grey clearfix']/ul/li[4]/a/text()").get())
            for i in range(1,num):
                yield Request(url='https://www.gtai.de/en/meta/search/66080!search;eNqVksFOwzAMht_F5yKtCAmp54kXgBvi4KbeyJQ6xU4GZdq7z90EhyGEuVnW99v5f-cAGwxUFLoD9FUjk-oNCuHSUEoUCg3QPUPkPWmBlwboIyTrWBV4Bx0gz3BsQGovMVzJfuJcUzI65MpFZi-uRmRRL57w3T15ohAxeXEKmfP4D59VSx7dD99ERg4kXn56RSV_5uNkx3qw6AcsMbPb9J64PM0T-c8lka5NQ3vb3t2v4HdV7XcGu7PKMmL5O9rLB13Cwi09xk9z0a4aeLsMsrVZbCdYJLQmDdCcy2Us8fAFCfKWvhUFF8n5HccT1ocWbA?page=' + str(i), callback=self.parse, meta=deepcopy(meta))
        except:
            pass

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        item['category1'] = 'Press Release'
        item['category2'] = None
        item['title'] = response.meta['title']
        item['body'] = ''.join(response.xpath(".//div[@class='richtext']/p//text()").extract())
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['time']
        return item
