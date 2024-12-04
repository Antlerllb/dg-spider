


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
# check: 凌敏 pass
class CnnewsSpider(BaseSpider):
    name = 'cnnews'
    website_id = 2032
    language_id = 1813
    proxy = '02'
    start_urls = ['https://cnnews.chosun.com/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        category1 = soup.select('#gnb a')
        for i in category1:
            url = 'https://cnnews.chosun.com' + i['href'] + '&cpage=1'
            yield scrapy.Request(url, callback=self.parse_page, meta={'category1': i.text.strip(), 'url': url, 'page': 1, 'left_page': 6})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if (soup.select_one('.articleList li') is None):  # 没有文章了，爬虫结束，退出函数
            self.logger.info("时间截止")
            return 1
        block = soup.select('.articleList li')
        for i in block:
            url = 'https://cnnews.chosun.com/client/news/' + i.select_one('a')['href']
            yield Request(url, callback=self.parse_item, meta=response.meta)
        response.meta['page'] += 1
        url = response.meta['url'].split('&cpage=')[0] + '&cpage=' + str(response.meta['page'])  # 页码+1后的url
        yield Request(url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('#title_title h4').text.strip()
        item['pub_time'] = soup.select_one('.date_text>p').text.split(' ')[-1][:10] + ' 00:00:00'
        item['images'] = []
        for i in soup.select('#articleBody img'):
            if i.get('src').startswith('http'):
                item['images'].append(i.get('src'))
            else:
                item['images'].append('https://cnnews.chosun.com' + i.get('src'))
        for i in soup.select_one('.realcons').text.strip().split('\n'):
            if not (i.strip() == '' or i.strip().startswith('▲')):  # 正文里的格式太乱了，一会空格一会▲
                item['body'] = i.strip()
                break
        item['abstract'] = item['body'].split('。')[0] + '。'
        return item
