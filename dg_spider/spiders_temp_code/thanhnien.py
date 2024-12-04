


from scrapy.http.request import Request
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

# author : 李玲宝
# check : 魏芃枫
# 网页部分403
class ThanhnienSpider(BaseSpider):
    name = 'thanhnien'
    website_id = 842
    language_id = 2242
    start_urls = ['https://thanhnien.vn/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.global-navigation > li')[1:]:  # 第一个超链接是视频，index从1开始
            for j in i.select('.global-navigation__children a'):
                if (j['href'].startswith('http')):
                    url = j['href']+'?trang=1'
                    yield scrapy.Request(url, callback=self.parse_page, meta={'category1': i.select_one('a')['title'], 'category2': j.text.strip(), 'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('.zone--timeline article')  # 每个新闻块
        flag = True
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.time').text.strip()
            last_time = f'{t[-4:]}-{t[-7:-5]}-{t[-10:-8]}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            response.meta['page'] += 1
            url = response.meta['url'].split('=')[0] + '=' + str(response.meta['page'])  # 页码+1后的url
            yield Request(url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('#storybox > h1').text.strip()
        item['abstract'] = soup.select_one('#chapeau > p').text
        t = soup.select_one('div.details__meta time').text
        item['pub_time'] = f'{t[-4:]}-{t[-7:-5]}-{t[-10:-8]}' + ' 00:00:00'
        item['images'] = []  # 文章第一个img的参数为‘src’，后面的img参数为‘data-src’
        flag = 0
        for i in soup.select('#abody img'):
            if (flag):
                item['images'] += [i['data-src']]
            else:
                item['images'] += [i['src']]
                flag = 1
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('#abody p'))
        return item
