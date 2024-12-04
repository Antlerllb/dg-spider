import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
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





from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

class PressocmSpider(BaseSpider):
    author = '王伟任'
    name = 'pressocm'
    website_id = 2699
    language_id = 2275
    start_urls = ['https://pressocm.gov.kh/archives/category/general-information-km/','https://pressocm.gov.kh/en/archives/category/general-news']
    lan_num = 2



    def parse(self, response):
            item = NewsItem(language_id=self.language_id)
            en_kong =''
            for num in range(0,9):
                pub_time_list = response.xpath('//span [@class="td-post-date"]/time/text()').extract()[num]
                pre_list = pub_time_list.split(' ')
                if pre_list[0] == '1':
                    pre_list[0] = '01'
                elif pre_list[0] == '2':
                    pre_list[0] = '02'
                elif pre_list[0] == '3':
                    pre_list[0] = '03'
                elif pre_list[0] == '4':
                    pre_list[0] = '04'
                elif pre_list[0] == '5':
                    pre_list[0] = '05'
                elif pre_list[0] == '6':
                    pre_list[0] = '06'
                elif pre_list[0] == '7':
                    pre_list[0] = '07'
                elif pre_list[0] == '8':
                    pre_list[0] = '08'
                elif pre_list[0] == '9':
                    pre_list[0] = '09'

                if pre_list[1] == 'January,':
                    pre_list[1] = '01'
                elif pre_list[1] == 'February,':
                    pre_list[1] = '02'
                elif pre_list[1] == 'March,':
                    pre_list[1] = '03'
                elif pre_list[1] == 'April,':
                    pre_list[1] = '04'
                elif pre_list[1] == 'May,':
                    pre_list[1] = '05'
                elif pre_list[1] == 'June,':
                    pre_list[1] = '06'
                elif pre_list[1] == 'July,':
                    pre_list[1] = '07'
                elif pre_list[1] == 'August,':
                    pre_list[1] = '08'
                elif pre_list[1] == 'September,':
                    pre_list[1] = '09'
                elif pre_list[1] == 'October,':
                    pre_list[1] = '10'
                elif pre_list[1] == 'November,':
                    pre_list[1] = '11'
                elif pre_list[1] == 'December,':
                    pre_list[1] = '12'
                pub_time = f'{pre_list[2]}-{pre_list[1]}-{pre_list[0]} 00:00:00'
                if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                    return
                website_hrefs = response.xpath('//h3 [@class="entry-title td-module-title"]/a/@href').extract()[num]

                title = response.xpath('//h3 [@class="entry-title td-module-title"]/a/text()').extract()[num]
                title = ''.join(title)
                title = title.replace("\u200b", "")
                title = title.replace("\xa0", "")
                title = title.replace("\n", "")

                abstract = response.xpath('//div[@ class="td-excerpt"]/text()').extract()[num]
                abstract = "".join(abstract)
                abstract = abstract.replace("\u200b", "")
                abstract = abstract.replace("\xa0", "")
                abstract = abstract.replace("\n", "")
                if abstract == en_kong:
                    abstract = "N"
                if abstract == None:
                    abstract = "N"
                response.meta['pub_time'] = pub_time
                response.meta['title'] = title
                response.meta['abstract'] = abstract
                response.meta['website_hrefs'] = website_hrefs

                if "en" in website_hrefs:
                    category1 = "General News"
                    language_id = 1866
                else:
                    category1 = "ព័ត៌មានទូទៅ"
                    language_id = 2275
                response.meta['language_id'] = language_id
                response.meta['category1'] = category1
                yield scrapy.Request(website_hrefs, callback=self.parse_item, meta=response.meta)

                if "en" in website_hrefs:
                    for page_num in range(2,98):
                        language_id = 1866
                        category1 = "General News"
                        response.meta['language_id'] = language_id
                        response.meta['category1'] = category1
                        next_url = f'https://pressocm.gov.kh/en/archives/category/general-news/page/{page_num}'
                        yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
                else:
                    for page_num in range(2,150):
                        language_id = 2275
                        category1 = "ព័ត៌មានទូទៅ"
                        response.meta['language_id'] = language_id
                        response.meta['category1'] = category1
                        next_url = f'https://pressocm.gov.kh/archives/category/general-information-km/page/{page_num}'
                        yield scrapy.Request(next_url, callback=self.parse, meta=response.meta)
    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        en_kong = ''
        abstract = response.meta['abstract']
        title = response.meta['title']
        pub_time = response.meta['pub_time']
        language_id = response.meta['language_id']
        category1 = response.meta['category1']
        body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/p/text()').extract()
        if body_list == en_kong:
            body_list = response.xpath('//div[@class ="youtube-embed"]/../p/text()').extract()
        if body_list == []:
            body_list = response.xpath('//div[@class ="youtube-embed"]/../p/text()').extract()
        if body_list == en_kong:
            body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/div/div/span/text()').extract()
        if body_list == []:
            body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/div/div/span/text()').extract()
        if body_list == en_kong:
            body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/div/div/div/text()').extract()
        if body_list == []:
            body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/div/div/div/text()').extract()
        if body_list == en_kong:
            body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/div/div/p/text()').extract()
        if body_list == []:
            body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/div/div/p/text()').extract()
        if body_list == en_kong:
            body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/div/div/text()').extract()
        if body_list == []:
            body_list = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/div/div/text()').extract()
        body = '\n'.join(body_list)
        body = body.replace("\u200b", "")
        body = body.replace("\xa0", "")
        if "\n" not in body_list:
            body = abstract +"\n"+body
        if body == "\n":
            body =abstract +"\n"+"N"

        images = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/img/@data-lazy-srcset').extract()
        if images !=[]:
            new =re.sub(r' \d+w','',images[0])
            images[0]=new
            images =images[0].split(", ")



        item['language_id']=language_id
        item['title'] = title
        item['body'] = body
        item['abstract'] = abstract
        item['images'] = images
        item['category1'] = category1
        item['pub_time'] = pub_time

        yield item

