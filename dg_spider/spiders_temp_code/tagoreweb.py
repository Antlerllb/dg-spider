


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
# 文章内容为经典诗歌小说，全都没有图片、时间（我统一给了1970-01-01 00:00:00），有的没有二级标题，
# check: 凌敏 pass
class TagorewebSpider(BaseSpider):
    name = 'tagoreweb'
    website_id = 1901
    language_id = 1779
    start_urls = ['https://tagoreweb.in/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.menu-sec li>a')[1:]:
            yield scrapy.Request('https://tagoreweb.in' + i['href'], callback=self.parse2, meta={'category1': i.text.strip().strip('*')})

    def parse2(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.select_one('.suchi_patra_area>ul') is not None:
            for i in soup.select('.suchi_patra_area>ul')[-1].select('a'):
                response.meta['url'] = 'https://tagoreweb.in' + i['href']
                yield scrapy.Request(response.meta['url'], callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.select_one('.title_area>h2') is not None:
            response.meta['category2'] = soup.select_one('.title_area>h2').text.strip().split('(')[0]
            for i in soup.select('.suchi_patra_area a'):
                yield scrapy.Request('https://tagoreweb.in' + i['href'], callback=self.parse_item, meta=response.meta)
        else:
            response.meta['category2'] = None
            yield scrapy.Request(response.meta['url'], callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['pub_time'] = OldDateUtil.get_now_datetime_str()
        item['images'] = []
        if item['category1'] == 'Songs':  # 板块之间的正文结构比较复杂
            item['title'] = soup.select_one('.content-right h2').text.split('(')[1].strip()[:-1]
            item['body'] = '\n'.join(i.text.strip().replace(' ', '') for i in soup.select('.content-right p') if i.text.strip() != '')
        elif soup.select_one('.content-right') is not None:
            item['title'] = soup.select_one('.content-right h2').text.split('(')[1].strip()[:-1]
            if soup.select_one('.content-right>p') is not None:
                item['body'] = '\n'.join(i.text.strip().replace(' ', '') for i in soup.select('.content-right>p') if i.text.strip() != '')
            else:
                item['body'] = '\n'.join(i.text.strip().replace(' ', '') for i in soup.select('.content-right>div>div') if i.text.strip() != '')
        else:
            item['title'] = soup.select_one('.divRight h2').text.split('(')[1].strip()[:-1]
            item['body'] = '\n'.join(i.strip().replace(' ', '') for i in soup.select_one('.divRight>div').text.strip().split('\n') if i.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
