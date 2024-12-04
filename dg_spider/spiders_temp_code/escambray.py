


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from copy import deepcopy

Spanish_MONTH = {
        'Ene': '01',
        'Feb': '02',
        'Mar': '03',
        'Abr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Ago': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dic': '12'
}


# author : 彭雨胜
# check: 凌敏 pass
class EscambraySpider(BaseSpider):
    name = 'escambray'
    website_id = 1297
    language_id = 2181
    start_urls = ['http://www.escambray.cu/']
    is_http = 1
    proxy = "02"

    def parse(self, response):
        meta = response.meta
        categories = response.xpath('//ul[@id="menu-principal"]/li/a')
        for category in categories:
            page_link = category.xpath('./@href').get()
            category1 = category.xpath('./text()').get().strip()
            meta['data'] = {
                'category1': category1
            }
            yield Request(url=page_link, callback=self.parse_page, meta=deepcopy(meta))

    def parse_page(self, response):
        flag = True
        articles = response.xpath('//div[@class="post-listing archive-box"]/article')
        meta = response.meta

        # tt = articles[-1].xpath('.//div[@class="postmeta"]/div//text()').getall()
        # last_time = "{}-{}-{}".format(tt[2].strip().split(" ")[1], Spanish_MONTH[tt[2].strip().split(" ")[0]], tt[1])
        # print(meta['data']['category1'], last_time)

        if OldDateUtil.time is not None:
            tt = articles[-1].xpath('.//div[@class="postmeta"]/div//text()').getall()
            last_time = "{}-{}-{}".format(tt[2].strip().split(" ")[1], Spanish_MONTH[tt[2].strip().split(" ")[0]], tt[1]) + " 00:00:00"
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                t = article.xpath('.//div[@class="postmeta"]/div//text()').getall()
                pub_time = "{}-{}-{}".format(t[2].strip().split(" ")[1], Spanish_MONTH[t[2].strip().split(" ")[0]], t[1]) + " 00:00:00"
                article_url = article.xpath('.//h2[@class="post-box-title"]/a/@href').get()
                title = article.xpath('.//h2[@class="post-box-title"]/a/text()').get().strip()
                meta['data']['pub_time'] = pub_time
                meta['data']['title'] = title
                yield Request(url=article_url, callback=self.parse_item, meta=deepcopy(meta))
        else:
            flag = False
            self.logger.info("时间截止")
        # 翻页
        if flag:
            if response.xpath('//span[@id="tie-next-page"]/a/@href').get() is None:
                self.logger.info("到达最后一页")
            else:
                next_page = response.xpath('//span[@id="tie-next-page"]/a/@href').get()
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
                '//div[@class="entry"]//p')] if paragraph.strip() != '' and paragraph.strip() != '\xa0']
        )
        item['abstract'] = response.xpath('//div[@id="article-summary"]/p/text()').get()
        item['images'] = response.xpath('//div[@class="post-inner"]//img/@src').getall()
        return item