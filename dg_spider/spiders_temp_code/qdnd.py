


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

# check:why

class QdndSpider(BaseSpider):
    name = 'qdnd'
    website_id = 840
    language_id = 2242
    start_urls = ['https://www.qdnd.vn/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.select('div.main-menu > ul > li')
        for i in menu[1:3] + menu[4:-1]:
            for j in i.select('ul a')[1:]:
                url = j['href'] + '/p/1'
                yield scrapy.Request(url, callback=self.parse_page, meta={'category1': i.select_one('a')['title'], 'category2': j['title'], 'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('.list-news-category article')[1:]  # 每个新闻块
        flag = True
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.hidden-xs').text
            last_time = f'{t[6:10]}-{t[3:5]}-{t[:2]}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            response.meta['page'] += 1
            url = response.meta['url'].split('/p/')[0] + '/p/' + str(response.meta['page'])  # 页码+1后的url
            yield Request(url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('h1.post-title').text.strip()
        item['abstract'] = soup.select_one('.post-summary').text.strip()
        # t = soup.select_one('span.post-subinfo').text.strip()
        # item['pub_time'] = f'{t[6:10]}-{t[3:5]}-{t[:2]}' + ' 00:00:00'
        item['pub_time'] = '2024-07-28' + ' 00:00:00'
        item['images'] = [img.get('src') for img in soup.select('.post-content img.imgtelerik')]
        item['body'] = soup.select_one('.post-content').text
        # item['body'] = '\n'.join(i.text.strip() for i in soup.select('.post-content p'))
        return item
