# encoding: utf-8
import re
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy


class AapcomauSpider(BaseSpider):
    name = 'aapcomau'
    author = '韩祎童'
    website_id = 2201
    language_id = 1866
    lan_num = 1
    start_urls = ['https://www.aap.com.au/factcheck/page/2/',
                  'https://www.aap.com.au/aapreleases/globenewswire/page/2/']

    indonesian_to_english_month = {
        'January': 'January',
        'February': 'February',
        'March': 'March',
        'April': 'April',
        'May': 'May',
        'June': 'June',
        'July': 'July',
        'August': 'August',
        'September': 'September',
        'October': 'October',
        'November': 'November',
        'December': 'December',
    }

    def parse_date(self, time_pre):
        for indo_month, eng_month in self.indonesian_to_english_month.items():
            time_pre = time_pre.replace(indo_month, eng_month)
        if len(time_pre.split()) == 3:
            date_obj = datetime.strptime(time_pre, "%d %B %Y")
            return date_obj.strftime("%Y-%m-%d 00:00:00")
        return None

    def parse(self, response):
        if "factcheck" in response.url:
            yield from self.parse_factcheck(response)
        elif "globenewswire" in response.url:
            yield from self.parse_globenewswire(response)

    def parse_factcheck(self, response):
        for i in range(1, 20):
            class_url = response.xpath('/html/body/div/main/div/div[2]/div[1]/div/div/div/div[2]/a[1]/@href').extract()[i]
            title = response.xpath('/html/body/div/main/div/div[2]/div[1]/div/div/div/div[2]/a[1]/h2/text()').extract()[i]
            abstract = response.xpath('/html/body/div/main/div/div[2]/div[1]/div/div/div/div[2]/p/text()').extract()[i].strip()
            response.meta.update({'images': [], 'title': title, 'abstract': abstract})
            yield scrapy.Request(class_url, callback=self.parse_item_factcheck, meta=response.meta)

        for num_first in range(3, 84):
            new_first_url = f'https://www.aap.com.au/factcheck/page/{num_first}/'
            yield scrapy.Request(new_first_url, callback=self.parse_factcheck)

    def parse_globenewswire(self, response):
        urls = response.xpath('/html/body/div/main/div[1]/div[2]/div/div/div/div[2]/a/@href').extract()
        titles = response.xpath('/html/body/div/main/div[1]/div[2]/div/div/div/div[2]/a/h2/text()').extract()
        abstracts = response.xpath('//*[@id="page-top"]/main/div[1]/div[2]/div/div/div/div[2]/p/text()').extract()
        abstract = next((text.strip() for text in abstracts if text.strip()), "No abstract available")

        for i in range(min(len(urls), len(titles))):
            class_url = urls[i]
            title = titles[i]
            response.meta.update({'images': [], 'title': title, 'abstract': abstract})
            yield scrapy.Request(class_url, callback=self.parse_item_globenewswire, meta=response.meta)

        for num_first in range(3, 82):
            new_first_url = f'https://www.aap.com.au/aapreleases/globenewswire/page/{num_first}/'
            yield scrapy.Request(new_first_url, callback=self.parse_globenewswire)

    def parse_item_factcheck(self, response):
        item = NewsItem(language_id=self.language_id)
        abstract = response.meta['abstract']
        body = response.xpath('/html/body/div[1]/main/section/div/div/div[1]/div[3]//text()').extract()
        body = [text.strip() for text in body if text.strip()]
        body = '\n\n'.join(body) if len(body) > 1 else f"{abstract}\n\n{body[0]}" if body else abstract

        time_pre = response.xpath('/html/body/div[1]/main/section/div/div[1]/div[1]/div[1]/div[1]/span[2]').extract_first()
        pub_time = self.parse_date(time_pre)

        item['language_id'] = self.language_id
        item['body'] = body
        item['title'] = response.meta['title']
        item['abstract'] = abstract
        item['images'] = response.meta['images']
        item['category1'] = "factcheck"
        item['pub_time'] = pub_time.strip() if pub_time and pub_time.strip() else None

        yield item

    def parse_item_globenewswire(self, response):
        item = NewsItem(language_id=self.language_id)
        abstract = response.meta['abstract']
        body = response.xpath('/html/body/div[1]/main/section/div/div[1]/div[1]/div[2]//text()').extract()
        body = [text.strip() for text in body if text.strip()]
        body = '\n\n'.join(body) if len(body) > 1 else f"{abstract}\n\n{body[0]}" if body else abstract

        time_pre = response.xpath('/html/body/div[1]/main/section/div/div[1]/div[1]/div[1]/div[1]/span[2]').extract_first()
        pub_time = self.parse_date(time_pre)

        item['language_id'] = self.language_id
        item['body'] = body
        item['title'] = response.meta['title']
        item['abstract'] = abstract
        item['images'] = response.meta['images']
        item['category1'] = "globenewswire"
        item['pub_time'] = pub_time.strip() if pub_time and pub_time.strip() else None

        yield item
