
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
from scrapy import FormRequest
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


# author 武洪艳
class MoaliGovSpider(BaseSpider):
    name = 'moali_gov'
    # allowed_domains = ['www.moali.gov.mm/']
    start_urls = ['https://www.moali.gov.mm/']  # https://www.moali.gov.mm/
    website_id = 1351  # 网站的id(必填)
    language_id = 2065  # 语言
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }
    # sql = {  # my本地 sql 配置
    #     'host': 'localhost',
    #     'user': 'root',
    #     'password': 'why520',
    #     'db': 'dg_crawler'
    # }

    # 这是类初始化函数，用来传时间戳参数

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        category_url = 'https://www.moali.gov.mm' + soup.select('.tb-megamenu-nav.nav.level-0.items-15 li a')[2].get('href')
        meta = {'category1': 'သတင်းများ  '}
        yield Request(url=category_url, callback=self.parse_page, meta=meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        a = re.split(r"[/ -]", soup.select('.view-content .views-field.views-field-created .field-content')[-1].text.strip())
        last_time = "{}-{}-{} {}:00".format(a[2], a[0], a[1], a[5])
        if OldDateUtil.time is None or OldDateUtil.format_time3(last_time) >= int(OldDateUtil.time):
            articles = soup.select('.view-content .views-field.views-field-view-node a')
            time = soup.select('.view-content .views-field.views-field-created .field-content')
            for i in range(len(time)):
                t = re.split(r"[/ -]", time[i].text.strip())  # 07/24/2018 - 10:43
                pubtime = "{}-{}-{} {}:00".format(t[2], t[0], t[1], t[5])
                article_url = 'https://www.moali.gov.mm' + articles[i].get('href')
                yield Request(url=article_url, callback=self.parse_item, meta={'pubtime': pubtime, 'category1': response.meta['category1']})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('.pager-next a') is None:
                self.logger.info("no more pages")
            else:
                next_page = 'https://www.moali.gov.mm' + soup.select_one('.pager-next a').get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('.container .row .col-md-12 h1').text
        item['pub_time'] = response.meta['pubtime']
        image_list = []
        imgs = soup.select('.field-item.even p img') if soup.select('.field-item.even p img') else None
        if imgs:
            for img in imgs:
                image_list.append(img.get('src'))
            item['images'] = image_list
        p_list = []
        if soup.select('.field-item.even p'):
            all_p = soup.select('.field-item.even p')
            for paragraph in all_p:
                p_list.append(paragraph.text)
            body = '\n'.join(p_list)
        item['body'] = body
        item['abstract'] = soup.select_one('.field-item.even p').text
        return item

