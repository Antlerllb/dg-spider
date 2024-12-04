


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author：张珍珍
class SnuacnSpider(BaseSpider):
    name = 'snuacn'
    num_list = ['328', '329']
    start_urls = [f'https://snuac.snu.ac.kr/?cat={i}' for i in num_list]

    website_id = 799
    language_id = 1991
    # 新闻量少

    def parse(self, response):
        flag = True
        url_list = response.xpath('//div[@class="item-content"]')
        for i in url_list:
            url = i.xpath('./h3/a/@href').get()
            title = i.xpath('./h3/a/@title').get()
            abstract = i.xpath('./div[@class="item-excerpt blog-item-excerpt"]/p/text() | ./div[@class="item-excerpt blog-item-excerpt"]/text()').get()
            category1 = i.xpath('./div[@class="item-meta blog-item-meta"]/span[2]/a/text()').get()
            yield Request(url=url, callback=self.parse_item, meta={'category1': category1, 'title': title, 'abstract': abstract})
        if flag:
            try:
                next_page = response.xpath('//a[@class="nextpostslink"]/@href').get()
                yield Request(url=next_page, callback=self.parse, meta=response.meta)
            except:
                self.logger.info("no more pages")

    def parse_item(self, response):
        if OldDateUtil.time is not None:
            t = response.xpath('//div[@class="item-meta single-post-meta content-pad"]/span[1]/text()').get().strip().replace(' ', '')
            tt = t.replace('년', '-').replace('월', '-').replace('일', '')
            last_time = tt + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['title'] = response.meta['title']
            item['abstract'] = response.meta['abstract']
            item['category1'] = response.meta['category1']
            item['category2'] = None
            t = response.xpath('//div[@class="item-meta single-post-meta content-pad"]/span[1]/text()').get().strip().replace(' ', '')
            tt = t.replace('년', '-').replace('월', '-').replace('일', '')
            item['pub_time'] = tt + ' 00:00:00'
            item['body'] = '\n'.join(['%s' % i.xpath('normalize-space(string(.))').get() for i in
                                      response.xpath('//div[@class="wpb_wrapper"]/p | //div[@class="single-post-content-text content-pad"]/ul/li | //div[@class="single-post-content-text content-pad"]/p '
                                                     '| //div[@class="wpb_wrapper"]/div | //div[@class="single-post-content-text content-pad"]/div | //*[@id="content"]/article/h2')])
            try:
                item['images'] = [i.xpath('./@src').get() for i in response.xpath('//div[@class="content-image"]/img | //div[@class="vc_single_image-wrapper   vc_box_border_grey"]/img')]
            except:
                item['images'] = ''
            yield item
        else:
            self.logger.info("时间截止")




