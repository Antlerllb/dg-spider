import re




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
# 我爬的是那个“乌尔都语”文档的网站，对接的同学说审核爬虫的人填id,那个id是我乱填的（不填会报错）
# 网站的新闻本来就没有二级标题
# check:凌敏 pass
class PakbjSpider(BaseSpider):
    name = 'pakbj'
    website_id = 2104
    language_id = 1866
    start_urls = ['http://www.pakbj.org']

    def parse(self, response):
        url = 'http://www.pakbj.org/index.php?m=content&c=index&a=lists&catid=12&page='
        yield scrapy.Request(url + '1', callback=self.parse_page, meta={'url': url, 'page': 1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('.news>.news_list')
        if (block == []):  # 没有文章了，爬虫结束，退出函数
            self.logger.info("时间截止")
            return 1
        if OldDateUtil.time is not None:
            t = block[-1].select_one('.news_cont>span').text.strip().split('.')
            last_time = f'{t[2]}-{t[1]}-{t[0]}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            response.meta['category1'] = soup.select_one('.news h1').text.strip()
            for i in block:
                tt = i.select_one('.news_cont>span').text.strip().split('.')
                response.meta['pub_time'] = f'{tt[2]}-{tt[1]}-{tt[0]}' + ' 00:00:00'
                yield Request(i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)
        response.meta['page'] += 1
        yield Request(response.meta['url'] + str(response.meta['page']), callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('.news-detail h2').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('.news-detail img')]
        item['body'] = ''
        for i in soup.select('.news-detail>p'):
            item['body'] += '\n'.join(j.strip() for j in i.text.split('\n') if j.strip() != '') + '\n'
        item['body'] = item['body'].strip()
        item['abstract'] = item['body'].split('\n')[0]
        if item['body']:
            return item
