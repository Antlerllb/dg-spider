
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
class JasaratSpider(BaseSpider):
    name = "jasarat"  # name的重命名
    author = '吴雨奔'
    website_id = 2318  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    allowed_domains = ["jasarat.com"]
    start_urls = ["https://www.jasarat.com/"]
    post_url = "https://www.jasarat.com/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=7.1.1"
    proxy = '02'
    # post请求的翻页控制
    category = {
        'الیکشن':'44753',
        'pakistan': '5',
        'world-news': '6',
        'sportsnews': '8',
        'education-health-women': '30169',
        'dilchasp-ajeeb': '34947',
        'scinenceandtechnology': '13',
        'ادارتی-صفحہ':'23113'
    }

    def parse(self, response):
        # 遍历字典并获取键和值
        for key, value in self.category.items():
            formdata = {
                "action": 'td_ajax_loop',
                "loopState[sidebarPosition]": "no_sidebar",
                "loopState[moduleId]": "2",
                "loopState[currentPage]": "2",
                "loopState[atts][category_id]": "29897",
                "loopState[ajax_pagination_infinite_stop]": "3",
                "loopState[server_reply_html_data]": ""
            }
            formdata['loopState[currentPage]'] = str(0)  # 默认请求第0页
            formdata['loopState[atts][category_id]'] = str(value)  # 请求的栏目分类

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
        page = data['server_reply_html_data']
        if page != "":
            page = etree.HTML(page)
            news_num = len(page.xpath('//div[@class="td-module-thumb"]'))
            for i in range(news_num):
                raw_date = page.xpath('//time[@class="entry-date updated td-module-date"]/text()')[i]
                dt = datetime.strptime(raw_date, "%B %d, %Y, %I:%M %p")
                pub_time = dt.strftime("%Y-%m-%d 00:00:00")  # 必须为00 00 00
                if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                    return
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
            formdata['loopState[currentPage]'] = str(current_page)
            # 继续发起下一页的 POST 请求
            yield scrapy.FormRequest(
                url=self.post_url,
                formdata=formdata,
                meta={'key': key, 'current_page': current_page, 'formdata': formdata},
                callback=self.parse_post,
               )
        else:
            current_page = 0
            return

    def parse_item(self, response):
        time.sleep(random.uniform(0.5, 0.6))
        item = NewsItem(response.meta['item'])
        article = response.xpath('//article/div[3]/p/text()').extract()
        if len(article) > 1:
            content = "\n".join(article)
        else:
            content = "\n" + item['abstract'] + "\n".join(article)
        item['body'] = content
        image = response.xpath('//div[@class="td-post-content"]/div/a/img/@src').extract_first()
        if image == '' or image is None or image == 'NULL':
            item['images'] = []
        else:
            item['images'] = [image]
        yield item

