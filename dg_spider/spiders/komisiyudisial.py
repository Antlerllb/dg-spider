


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy


# author : 宋宇涛
class KomisiyudisialSpider(BaseSpider):
    name = 'komisiyudisial'
    website_id = 110
    language_id = 1952
    start_urls = ['https://komisiyudisial.go.id']
    month = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'Mei': 5,
        'Jun': 6,
        'Jul': 7,
        'Agu': 8,
        'Sep': 9,
        'Okt': 10,
        'Nov': 11,
        'Des': 12
    }

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//*[@id="boxed-bg"]/div[1]/div/header/div/div/div/div[2]/div/div[2]/div/nav/ul/li[6]/a')
        for category in categories:
            page_link = self.start_urls[0]+category.xpath('./@href').get()
            category1 = category.xpath('./text()').get().strip()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))
    def parse_page(self, response):
        flag = True
        articles = response.xpath('//*[@id="main"]/div/div/div[1]/div[1]/ul/li')
        meta = response.meta
        if OldDateUtil.time is not None:
            t = articles[-1].xpath('.//div[@class="meta"]/span[1]/text()').get().split()
            last_time = "{}-{}-{} {}".format(t[2],self.month[t[1]],t[0],t[3])
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.xpath('.//div[@class="meta"]/span[1]/text()').get().split()
                pub_time = "{}-{}-{} {}".format(tt[2],self.month[tt[1]],tt[0],tt[3])
                article_url = self.start_urls[0]+article.xpath('./a/@href').get()
                title = article.xpath('./a//strong/text()').get()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath(
                    '//*[@id="main"]/div/div/div[1]/div[2]/ul/nav/ul/li/a/@href')[-1] is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath(
                    '//*[@id="main"]/div/div/div[1]/div[2]/ul/nav/ul/li/a/@href')[-1].get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta))
    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                '//*[@id="main"]/div/div/div[1]/article[1]/div[3]')]]
        )
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = [self.start_urls[0]+response.xpath('//*[@id="main"]/div/div/div[1]/article[1]/div[2]/a/img/@src').get()]
        return item