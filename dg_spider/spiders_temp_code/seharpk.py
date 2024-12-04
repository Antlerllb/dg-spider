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


import json
from lxml import etree
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy


class SeharpkSpider(BaseSpider):
    name = "seharpk"
    author = '吴雨奔'
    website_id = 2319  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    allowed_domains = ["sehar.pk"]
    start_urls = ["https://sehar.pk"]
    post_url = 'https://sehar.pk/wp-admin/admin-ajax.php'
    proxy =  '02'

    def parse(self, response):
        page_list = response.xpath('//ul[@id="menu-tielabs-main-menu"]/li/a')

        for index, column in enumerate(page_list):

            category1 = column.xpath('./text()').extract_first()
            url = column.xpath('./@href').extract_first()
            # print(index, category1)
            # if(index == 0):
            #     formdata = {
            #         "action": "tie_blocks_load_more",
            #         "block[order]": "latest",
            #         "block[number]": "20",
            #         "block[pagi]" : "load-more",
            #         "block[excerpt]": "true",
            #         "block[post_meta]": "true",
            #         "block[breaking_effect]": "reveal",
            #         "block[sub_style]": "big",
            #         "block[style]": "default",
            #         "page": "0",
            #         "width": "single"
            #     }
            #     yield scrapy.FormRequest(
            #         url=self.post_url,
            #         formdata=formdata,
            #         meta={'category1': category1,'current_page':0,'formdata':formdata},
            #         callback= self.parse_post,
            #     )

            if (index != 18 and index != 17 and index != 15 and index != 0):
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_get,
                    meta={'category1': category1}
                )

    def parse_post(self, response):
        category1 = response.meta['category1']
        current_page = response.meta['current_page']
        formdata = response.meta['formdata']
        # print(response.text)
        # raw_string = response.text
        # unescaped_string = bytes(raw_string, "utf-8").decode("unicode_escape")

        data = json.loads(response.text)
        data = json.loads(data)
        page = data["code"]

        if page != "":
            page = etree.HTML(page)
            news_list = page.xpath('//h2[@class="post-title"]')
            for news in news_list:
                raw_date = news.xpath('./../div/span[2]')
                if 'ago' in raw_date:
                    dt = datetime.strptime(raw_date, "%B %d, %Y, %I:%M %p")
                    pub_time = dt.strftime("%Y-%m-%d 00:00:00")  # 必须为00 00 00
                if 1 == 1:
                    pass
                # if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                #     return
                else:
                    item = {}
                    item['category1'] = key
                    item['title'] = page.xpath('//h3[@class="entry-title td-module-title"]/a/text()')[i]
                    item['pub_time'] = dt.strftime("%Y-%m-%d %H:%M:%S")
                    link = page.xpath('//h3[@class="entry-title td-module-title"]/a/@href')[i]
                    item['abstract'] = page.xpath('//div[@class="td-excerpt"]/text()')[i]
                    yield scrapy.Request(
                        url=link,
                        callback=self.parse_item,
                        meta={'item': item}
                    )
            current_page = current_page + 1
            formdata['page'] = str(current_page)
            # 继续发起下一页的 POST 请求
            yield scrapy.FormRequest(
                url=self.post_url,
                formdata=formdata,
                meta={'category1': category1, 'current_page': 0, 'formdata': formdata},
                callback=self.parse_post,
            )
        else:
            current_page = 0
            return

    def parse_get(self, response):
        category1 = response.meta['category1']
        news_list = response.xpath('//ul[@id="posts-container"]/li')
        if news_list is not None and news_list != '':
            for news in news_list:
                url = news.xpath('.//a[@class="more-link button"]/@href').extract_first()
                url_parts = url.split('/')
                pub_time = url_parts[3] + '-' + url_parts[4] + '-' + url_parts[5] + ' 00:00:00'
                if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                    continue
                else:
                    item = {}
                    item['category1'] = category1
                    item['title'] = news.xpath('.//h2/a/text()').extract_first().replace('\xa0', ' ')
                    if 'Mechanism' in item['title'] or 'Role of BOP' in item['title'] or 'CRIME AND' in item['title'] or 'Gadgets World' in item['title'] or 'Lockdown' in item['title'] or 'Circular debt crisis in Pakistan' in item['title'] or 'Trade and travel' in item['title']:
                        item['language_id'] = 1866
                    item['pub_time'] = pub_time
                    item['abstract'] = news.xpath('.//p[@class="post-excerpt"]/text()').extract_first().replace('\xa0', ' ')
                    # print('url:', url, 'item', item)
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_item,
                        meta={'item': item}
                    )

        # 翻页按钮：>
        next_url = response.xpath('//span[@class="last-page first-last-pages"]/a/@href').extract_first()
        # 判断终止条件
        if next_url is not None and next_url != '':
            # 最后一页为：javascript:void(0)
            # 符合条件不停地翻页
            # next_url = response.urljoin(part_url)
            # 构建请求对象并且返回给引擎
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_get,
                meta={'category1': category1}
            )

    def parse_item(self, response):
        item = NewsItem(response.meta['item'])
        article = response.xpath('//p[@class="has-text-align-right"]//text()').extract()
        if len(article) > 1:
            content = "\n".join(article)
        else:
            content = "\n" + item['abstract'] + "\n".join(article)
        item['body'] = content
        image = response.xpath('//article//img/@src').extract_first()
        if image == '' or image is None or image == 'NULL':
            item['images'] = []
        else:
            item['images'] = [image]
        yield item