
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
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

import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import random
class PakobserverSpider(BaseSpider):
    name = "pakobserver"  # name的重命名
    author = '吴雨奔'
    website_id = 2313  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    allowed_domains = ["pakobserver.net"]
    start_urls = ["https://pakobserver.net/"]
    post_url = "https://pakobserver.net/?ajax-request=jnews"
    # post请求的翻页控制

    category = {
        'topNews': '19',
        'pakistan': '20',
        'business': '25',
        'sports': '28',
        'international': '77',
        'lifestyle': '910',
        'cpec': '29',
        'article': '31',
        'kashmir': '78',
        'tech':'912',
        'pakistan-islamabad':'21',
        'pakistan-lahore': '23',
        'pakistan-karachi': '22',
    }

    def parse(self, response):
        # 遍历字典并获取键和值
        for key, value in self.category.items():
            formdata = {
                "lang": "en_US",
                "action": "jnews_module_ajax_jnews_block_4",
                "module": "true",
                "data[filter]": "0",
                "data[filter_type]": "all",
                "data[current_page]": '0',
                "data[attribute][header_type]": "heading_6",
                "data[attribute][header_filter_text]": "All",
                "data[attribute][post_type]": "post",
                "data[attribute][content_type]": "all",
                "data[attribute][sponsor]": "false",
                "data[attribute][number_post]": "10",
                "data[attribute][post_offset]": "5",
                "data[attribute][unique_content]": "disable",
                "data[attribute][included_only]": "false",
                "data[attribute][include_category]": "271",
                "data[attribute][sort_by]": "latest",
                "data[attribute][date_format]": "default",
                "data[attribute][excerpt_length]": "20",
                "data[attribute][excerpt_ellipsis]": "...",
                "data[attribute][pagination_mode]": "loadmore",
                "data[attribute][pagination_number_post]": "10",
                "data[attribute][pagination_scroll_limit]": "0",
                "data[attribute][ads_type]": "disable",
                "data[attribute][ads_position]": "1",
                "data[attribute][google_desktop]": "auto",
                "data[attribute][google_tab]": "auto",
                "data[attribute][google_phone]": "auto",
                "data[attribute][boxed]": "false",
                "data[attribute][boxed_shadow]": "false",
                "data[attribute][column_width]": "auto",
                "data[attribute][paged]": "1",
                "data[attribute][pagination_align]": "center",
                "data[attribute][pagination_navtext]": "false",
                "data[attribute][pagination_pageinfo]": "false",
                "data[attribute][box_shadow]": "false",
                "data[attribute][push_archive]": "true",
                "data[attribute][column_class]": "jeg_col_2o3",
                "data[attribute][class]": "jnews_block_4"
            }
            formdata['data[current_page]'] = str(0)  # 默认请求第0页
            formdata['data[attribute][include_category]'] = str(value)  # 请求的栏目分类

            yield scrapy.FormRequest(
                url=self.post_url,
                formdata=formdata,
                meta={'key': key,'current_page':0,'formdata':formdata},
                callback=self.parse_post
            )

    def parse_post(self, response):
        # post请求的解析方法
        key = response.meta['key']
        current_page = response.meta['current_page']
        formdata = response.meta['formdata']

        data = json.loads(response.text)
        page = data['content']
        if page != "<div class='jeg_empty_module'>No Content Available</div>":
            page = etree.HTML(page)
            news_num = len(page.xpath('//article/div[2]/h3/a/text()'))
            for i in range(news_num):
                raw_date = page.xpath('//div[@class="jeg_meta_date"]/a/text()')[i]
                dt = datetime.strptime(raw_date, " %B %d, %Y")
                pub_time = dt.strftime("%Y-%m-%d 00:00:00")  # 必须为00 00 00
                if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                    return
                else:
                    item = {}
                    item['category1'] = key
                    item['title'] = page.xpath('//article/div[2]/h3/a/text()')[i]
                    link = page.xpath('//article/div[2]/h3/a/@href')[i]
                    item['pub_time'] = pub_time
                    abstract = page.xpath('//div[@class="jeg_post_excerpt"]/p/text()')[i]
                    if abstract != '':
                        item['abstract'] = page.xpath('//div[@class="jeg_post_excerpt"]/p/text()')[i]
                    else:
                        item['abstract'] = ''
                    yield scrapy.Request(
                        url=link,
                        callback=self.parse_item,
                        meta={'item': item}
                    )

                # else:
                #     continue
            current_page = current_page + 1
            formdata['data[current_page]'] = str(current_page)
            # 继续发起下一页的 POST 请求
            yield scrapy.FormRequest(
                url=self.post_url,
                formdata=formdata,
                meta={'key': key, 'current_page': current_page, 'formdata': formdata},
                callback=self.parse_post
            )
        else:
            current_page = 0
            return

    def parse_item(self, response):
        # time.sleep(random.uniform(0.01, 0.2))
        item = NewsItem(response.meta['item'])
        # item['pub_time'] = dt.strftime("%Y-%m-%d %H:%M:%S")
        article = response.xpath('/html/body/div[3]/div[6]/div[1]/div[1]/div/div/div/div[4]/div[1]/div/div[4]/div[2]/p/text()').extract()
        if len(article) > 1:
            content = "\n".join(article)
        else:
            content = "\n" + item['abstract'] + "\n".join(article)
        item['body'] = content
        image = response.xpath('//div[@class="jeg_inner_content"]/div/a/@href').extract_first()
        if image == None:
            item['images'] = []
        else:
            item['images'] = [image]
        item['language_id'] = 1866
        yield item

