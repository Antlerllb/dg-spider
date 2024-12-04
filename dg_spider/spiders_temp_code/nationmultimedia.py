


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
# check：凌敏 60%报403
class NationmultimediaSpider(BaseSpider):
    name = 'nationmultimedia'
    website_id = 223
    language_id = 1866
    start_urls = ['https://api.nationthailand.com/api/v1.0/navigations/menu-nav']

    def parse(self, response):
        response = response.json()  # 收取json文件
        for i in response[:-2]:
            for j in i['sub']:  # i['sub']存放二级标题
                page = 1
                url = 'https://api.nationthailand.com/api/v1.0' + j['link'].replace('category', 'categories') + '?page=' + str(page)
                yield scrapy.Request(url, callback=self.parse_page, meta={'category1': i['nameEng'], 'category2': j['nameEng'], 'page': page, 'url': url})
            # 如果没有二级标题，i['sub']为空，不会进入for循环
            url = 'https://api.nationthailand.com/api/v1.0/' + i['link'].replace('category', 'categories') + '?page=' + str(page)
            yield scrapy.Request(url, callback=self.parse_page, meta={'category1': i['nameEng'],'category2': None, 'page': page, 'url': url})


    def parse_page(self, response):
        meta = response.meta
        response = response.json()  # 收取json文件
        if (response['data'] == []):  # 没有文章了，爬虫结束，退出函数
            self.logger.info("时间截止")
            return 1
        flag = True
        if OldDateUtil.time is not None:
            t = response['data'][-1]['published_at']
            last_time = f'{t[0:4]}-{t[5:7]}-{t[8:10]}' + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for i in response['data']:
                t = response['data'][-1]['published_at']  # 正文里的时间转得很麻烦，在这就存入meta
                meta['pub_time'] = f'{t[0:4]}-{t[5:7]}-{t[8:10]}' + ' 00:00:00'
                yield Request('https://nationthailand.com' + i['link'], callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            meta['page'] += 1
            url = meta['url'].split('=')[0] + '=' + str(meta['page'])  # 页码+1后的url
            yield Request(url, callback=self.parse_page, meta=meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        if (response.meta['category2'] is not None):
            item['category2'] = response.meta['category2']
        item['title'] = soup.select_one('.detail-title-header').text
        item['abstract'] = soup.select_one('.content-blurb').text
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('#contents img')]
        item['body'] = '\n'.join(i.text.strip() for i in soup.select('#contents p'))
        return item
