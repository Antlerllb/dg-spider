


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy


# author : 宋宇涛
class KemendesaSpider(BaseSpider):
    name = 'kemendesa'
    website_id = 108
    language_id = 1952
    start_urls = ['https://kemendesa.go.id/berita/']

    month = {
        'Januari': 1,
        'Februari': 2,
        'Maret': 3,
        'April': 4,
        'Mei': 5,
        'Juni': 6,
        'Juli': 7,
        'Agustus': 8,
        'September': 9,
        'Oktober': 10,
        'Nopember': 11,
        'Desember': 12
    }
    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//nav[@class="navbar navbar-fix-top nopadding kmd-navbar"]/div[@class="container nopadding-padding"]/div[2]/ul/li[1]/a')
        for category in categories:
            page_link = self.start_urls[0]+response.xpath('//*[@id="kmd-wrapper"]/div[1]/div/div[3]/div[1]/div[1]/div/div/a/@href').get()
            category1 = category.xpath('./text()').get()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))
    def parse_page(self, response):
        flag = True
        articles =response.xpath('//div[@class="col-md-8 nopadding col-satker"]//div[@class="nav nav-tabs kmd-tabs-phill"]/div')[1:]
        meta = response.meta
        if OldDateUtil.time is not None:
            t = articles[-1].xpath('./div[2]/p[1]/text()').get().split()
            last_time = "{}-{}-{}".format(t[-1], self.month[t[-2]], t[-3]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.xpath('./div[2]/p[1]/text()').get().split()
                pub_time = "{}-{}-{}".format(tt[-1], self.month[tt[-2]], tt[-3]) + ' 00:00:00'
                article_url = article.xpath('./div[2]/h5/a/@href').get()
                title = article.xpath('./div[2]/h5/a/text()').get().strip()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath(
                    '//div[@class="pagination pagination-centered"]/ul/li').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath(
                    '//div[@class="pagination pagination-centered"]/ul/li')[-2]
                next_page=next_page.xpath("./a/@href").get()
                yield Request(url=next_page, callback=self.parse_page, meta=deepcopy(meta))
    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = meta['data']['category1']
        item['category2'] = None
        item['title'] = meta['data']['title']
        item['pub_time'] = meta['data']['pub_time']
        item['body'] = '\n'.join(
            [paragraph.strip() for paragraph in ["".join(text.xpath('./text()').getall()) for text in response.xpath(
                '//p')]]
        ).strip()
        item['abstract'] = "".join([i.strip() for i in item['body'].strip().split('\n')])
        item['images'] = [response.xpath('//*[@id="wrapper"]/img/@src').get()]
        return item