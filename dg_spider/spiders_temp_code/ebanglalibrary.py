


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
# 文章内容为经典诗歌小说，全都没有图片、二级标题、时间（我统一给了1970-01-01 00:00:00）
# 前一分钟会报一些403，麻烦等一会，后面会爬到文章的
# check: 凌敏 pass
class EbanglalibrarySpider(BaseSpider):
    name = 'ebanglalibrary'
    website_id = 1911
    language_id = 1779
    proxy = '02'
    start_urls = ['https://www.ebanglalibrary.com/%e0%a6%b2%e0%a7%87%e0%a6%96%e0%a6%95-%e0%a6%b0%e0%a6%9a%e0%a6%a8%e0%a6%be/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.entries-wrap a'):
            url = i['href'] + 'page/'
            yield scrapy.Request(url + '1/', callback=self.parse_page, meta={'category1': i.text.strip(), 'page': 1, 'url': url})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.entries-wrap a'):
            yield scrapy.Request(i['href'], callback=self.parse_item, meta=response.meta)
        if soup.select_one('.pagination-next') is not None:
            response.meta['page'] += 1
            yield scrapy.Request(response.meta['url'] + str(response.meta['page']) + '/', callback=self.parse_page, meta=response.meta)
        else:
            self.logger.info("时间截止")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.select_one('.entry-content p') is not None:
            item = NewsItem(language_id=self.language_id)
            item['category1'] = response.meta['category1']
            if '–' in soup.select_one('.page-header-title').text:
                item['title'] = soup.select_one('.page-header-title').text.strip().split(' ')[0].strip()
            else:
                item['title'] = soup.select_one('.page-header-title').text.split(' ')[-1].strip()
            item['pub_time'] = OldDateUtil.get_now_datetime_str()
            item['images'] = []
            item['body'] = '\n'.join(i.text.strip() for i in soup.select('.entry-content p') if i.text.strip() != '')
            item['abstract'] = item['body'].split('\n')[0]
            return item
