# encoding: utf-8



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

month = {
        'جنوری': '01',
        'فروری': '02',
        'مارچ': '03',
        'اپریل': '04',
        'مئی': '05',
        'جون': '06',
        'جولائی': '07',
        'اگست': '08',
        'ستمبر': '09',
        'اکتوبر': '10',
        'نومبر': '11',
        'دسمبر': '12'
    }
# author:胡冠锋
class roznama92newsSpider(BaseSpider):
    name = 'roznama92news'
    allowed_domains = ['www.roznama92news.com']
    start_urls = ['https://www.roznama92news.com/']

    # 下面这两个id都需要审核人修改，网站列表里没标明这俩id
    website_id = 988
    language_id = 1866

    def parse(self, response):
        li_list = response.xpath('/html/body/header/div[3]/div/div/div/nav/div/div[2]/ul/li[1]/ul/li')[:]
        #li_list = response.xpath('//ul[@class="dropdown-menu show"]/li')[:]
        for li in li_list:
            url = 'https://www.roznama92news.com' + li.xpath('./a/@href').get()
            category1 = li.xpath('./a/text()').get()
            yield Request(url, callback=self.parse_page, meta={'category1': category1})

    def parse_page(self, response):
        flag = True
        if OldDateUtil.time is not None:
            #time = response.xpath('//span[@class="pull-right date"]/b/text()').get()
            #time = list(response.xpath('.//span[@class="pull-right date"]/b/text()').get().replace('ء', '').replace('xa0', '').replace('\\', ' ').split(' '))
            time = list(response.xpath('.//span[@class="pull-right date"]/b/text()').get().replace('ء', '').split('\xa0'))
            last_time = time[3] + '-' + month[time[2]] + '-' + time[1] + "00:00:00"

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= int(OldDateUtil.time):
            div_list = response.xpath('/html/body/div[1]/div/div/div/div/div[1]/div[@class="post clearfix"]')[:]
            #div_list = response.xpath('//div[@class="post clearfix"]')
            for i in div_list:
                url = 'https://www.roznama92news.com' + i.xpath('.//div[@class="col-sm-12"]/h2/a/@href').get()
                time = list(response.xpath('.//span[@class="pull-right date"]/b/text()').get().replace('ء', '').split('\xa0'))
                #time = response.xpath('.//span[@class="pull-right date"]/b/text()').get().replace('ءxa0', '').split('\xa0')
                pub_time = time[3] + '-' + month[time[2]] + '-' + time[1] + " " + "00:00:00"
                #print(pub_time)
                try:
                    response.meta['title'] = i.xpath('.//div[@class="col-sm-12"]/h2/a/text()').get().strip()
                except:
                    response.meta['title'] = []
                try:
                    response.meta['abstract'] = i.xpath('.//div[@class="post-content"]/text()').get().strip()
                except:
                    response.meta['abstract'] = []
                response.meta['pub_time'] = pub_time
                yield Request(url, callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:  # 也就是时间未截止翻页
            next_page = 'https://www.roznama92news.com' + response.xpath('//li[@class="next"]/a/@href').get()
            yield Request(url=next_page, callback=self.parse_page, meta=response.meta)  # 默认回调给parse()
        else:
            self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['abstract'] = response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        # item['category2'] = None
        #//text()获取所有文本(包括p标签),如果去掉所有空行后不为空说明有正文
        item['body'] = '\n'.join(['%s' % i.get().strip() for i in response.xpath('//div[@class="post-content"]//text()') if '%s' % i.get().strip() != ''])
        # 如果前面没有摘要则默认为正文第一句
        if not item['abstract']:
            item['abstract'] = item['body'].split('\n')[0]
        # try:
        item['images'] = ['https://www.roznama92news.com' + i.xpath('./@src').get() for i in response.xpath('/html/body/div[1]/div/div[1]/div[1]/div[1]/div/div/img')]
        # except:
        #     item['images'] = []
        yield item
