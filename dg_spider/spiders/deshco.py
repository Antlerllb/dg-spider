


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re

# encoding: utf-8

# 英语月份对照表
ENGLISH_MONTH = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sept': '09',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

# author : 李玲宝
# 有的新闻本来就没有二级标题
# check：凌敏 pass 常报403
class DeshcoSpider(BaseSpider):
    name = 'deshco'
    website_id = 1894
    language_id = 1779
    # proxy = '02'
    start_urls = ['https://www.desh.co.in/']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select('.navbar-nav>li'):
            for j in i.select('li>ul a'):
                yield scrapy.Request(j['href'], callback=self.parse2, meta={'category1': i.select_one('a').text.strip(), 'category2': j.text.strip(), 'page': 1})
            if (i.select_one('li>ul a') is None):
                yield scrapy.Request(i.select_one('a')['href'], callback=self.parse2, meta={'category1': i.select_one('a').text.strip(), 'category2': None, 'page': 1})

    def parse2(self, response):
        json_url = re.search(r'https://www.desh.co.in/api/jsonws.*?page-no', response.text).group() + '/'
        response.meta['url'] = json_url
        yield scrapy.Request(json_url + '1', callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        article = response.json()
        if (article == []):  # 没有文章了，爬虫结束，退出函数
            self.logger.info("时间截止")
            return 1
        if OldDateUtil.time is not None and article[0].get('pub_time') is not None:
            t = article[-1]['created_at'].split(' ')
            last_time = f'{t[2]}-{OldDateUtil.EN_1866_DATE[t[0]]}-{t[1][:-1]}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in article:
                url = 'https://www.desh.co.in/api/jsonws/deshfrontservices.deshfronts/get-story-page-content/article-id/' + i['id']
                if i.get('created_at') is not None:
                    tt = i['created_at'].split(' ')
                    response.meta['pub_time'] = f'{tt[2]}-{OldDateUtil.EN_1866_DATE[tt[0]]}-{tt[1][:-1]}' + ' 00:00:00'
                else:
                    response.meta['pub_time'] = '1970-01-01 00:00:00'
                yield Request(url, callback=self.parse_item, meta=response.meta)
        response.meta['page'] += 1
        yield Request(response.meta['url'] + str(response.meta['page']), callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        article = response.json()
        if article.get('imageContent').get('title') is not None and article.get('imageContent').get('decsription') is not None:
            item = NewsItem(language_id=self.language_id)
            item['category1'] = response.meta['category1']
            item['title'] = article.get('imageContent').get('title')
            item['abstract'] = article.get('imageContent').get('decsription')
            item['pub_time'] = response.meta['pub_time']
            item['images'] = ['https://www.desh.co.in' + article['imageContent']['img']]
            soup = BeautifulSoup(article.get('content'), 'html.parser')
            item['body'] = '\n'.join(i.text.strip() for i in soup.select('p') if i.text.strip() != '')
            return item
