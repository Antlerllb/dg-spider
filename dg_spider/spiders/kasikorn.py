


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

month = {
    'มกราคม': '01',
    'กุมภาพันธ์': '02',
    'มีนาคม': '03',
    'เมษายน': '04',
    'พฤษภาคม': '05',
    'มิถุนายน': '06',
    'กรกฎาคม': '07',
    'สิงหาคม': '08',
    'กันยายน': '09',
    'ตุลาคม': '10',
    'พฤศจิกายน': '11',
    'ธันวาคม': '12'
}
#author 黄华煜
class KasikornSpider(BaseSpider):
    name = 'kasikorn'
    allowed_domains = ['kasikornresearch.com']
    start_urls = ['https://kasikornresearch.com/th']
    website_id = 2919
    language_id = 2208

    def parse(self, response):
        li_list = response.xpath('//*[@id="navmain"]/ul/li')[1:5]
        for li in li_list:
            category1 = li.xpath('./a[1]//text()').get()
            menu_list = li.xpath('.//div[@class="col-xs-4"]/div/ul/li')
            for menu in menu_list:
                category2 = menu.xpath('./a/text()').get()
                url = "https://www.kasikornresearch.com" + menu.xpath('./a/@href').get()
                yield Request(url, callback=self.parse_page, meta={'category1': category1, 'category2': category2})


    def parse_page(self,response):
        flag = True
        if OldDateUtil.time is not None:
            new_time = response.xpath('.//div[@class ="t-body"]/div[1]//div[@class ="meta"]/p[1]/text()').get().split(' ')
            last_time = str(int(new_time[2]) - 543) + '-' + month[new_time[1]] + '-' + new_time[0] + " 00:00:00"

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            article_list = response.xpath('.//div[@class ="t-body"]/div')
            for article in article_list:
                the_time = article.xpath('.//div[@class ="meta"]/p[1]/text()').get().split(' ')
                response.meta['pub_time'] = str(int(the_time[2])-543) + '-' + month[the_time[1]] + '-' + the_time[0] + " 00:00:00"
                response.meta['title'] = article.xpath('.//div[@class ="meta"]/h3/a/text()').get()
                response.meta['abstract'] = article.xpath('.//div[@class ="meta"]/p[3]//text()').get()
                response.meta['image'] = "https://www.kasikornresearch.com" + article.xpath('.//div[@class ="image"]/a/img/@src').get()
                url = "https://www.kasikornresearch.com" + article.xpath('.//div[@class ="image"]/a/@href').get()
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")

        if flag:
            self.logger.info("no more pages")

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        images_list = []
        images_list.append(response.meta['image'])
        figure_list = response.xpath('//div[@class ="art-image"]/img')
        for figure in figure_list:
            images_list.append("https://www.kasikornresearch.com" + figure.xpath('./@src').get())
        item['images'] = images_list
        item['body'] = '\n'.join(['%s' % i.xpath('string(.)').get() for i in response.xpath('//div[@class="art-content entrycontent"]/p |//div[@class="art-content entrycontent"]/ul | //div[@class="art-content entrycontent"]/div[(@style="text-align:justify;")]')])
        yield item

