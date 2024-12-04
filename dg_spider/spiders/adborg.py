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
class AdborgSpider(BaseSpider):
    name = 'adborg'
    website_id = 2101
    language_id = 1866
    start_urls = ['https://www.adb.org/search0/type/article/type/blog/type/event/type/inside_adb/type/news/type/oped/type/photo_essay/type/result/type/speech?page=0']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        url = 'https://www.adb.org/search0/type/article/type/blog/type/event/type/inside_adb/type/news/type/oped/type/photo_essay/type/result/type/speech?page='
        sumPage = soup.select_one('.current-search-item').text.strip().split(' ')[-1]
        for i in range(0, int(sumPage) // 20 + 2):
            yield scrapy.Request(url + str(i), callback=self.parse_page, meta={})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('.views-list>ul>li')
        if OldDateUtil.time is not None:
            last_time = block[-1].select_one('.date-display-single')['content'][:10] + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in block:
                response.meta['category1'] = i.select_one('.meta').text.strip().split(' ')[-1]
                response.meta['pub_time'] = i.select_one('.date-display-single')['content'][:10] + ' 00:00:00'
                yield Request('https://www.adb.org' + i.select_one('a')['href'], callback=self.parse_item, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = soup.select_one('h1').text.strip()
        item['pub_time'] = response.meta['pub_time']
        imgArr = soup.select('.col-lg-9 img') + soup.select('article .img-responsive') + soup.select('.article-img img') + soup.select('.adb-main-wrapper img')
        if soup.select_one('.col-lg-8') is not None:
            imgArr += soup.select_one('.col-lg-8').select('img')
        item['images'] = [img.get('src') for img in imgArr]
        if soup.select_one('.col-lg-8') is not None:
            bodyTag = '.col-lg-8'
        elif soup.select_one('.col-md-8') is not None:
            bodyTag = '.col-md-8'
        elif soup.select_one('.article-main') is not None:
            bodyTag = '.article-main'
        item['body'] = '\n'.join(i.strip() for i in soup.select_one(bodyTag).text.split('\n') if i.strip() != '')
        item['abstract'] = item['body'].split('\n')[0]
        return item
