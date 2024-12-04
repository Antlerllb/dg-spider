import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re


class CubacuSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    is_http = 1
    name = 'cubacu'  # name的重命名
    language_id = 2181
    website_id = 1290  # id一定要填对！
    start_urls = ['http://www.cuba.cu/home/news_by_category/todas/16/1']
    page = 1
    cnt1 = 0
    cnt2 = 0

    # print(1)
    @staticmethod
    def formalize(category, title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ').replace('\n', '')
        title = re.sub(' +', ' ', title).strip().strip('\n').replace('\n', '')
        body = re.sub('<br>.*?<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', '').replace('\t', '').replace('\u3000', ' ').replace(' ', ' ').replace('　', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = re.sub(' +', ' ', body).strip()
        body = body.strip().split('\n')
        body_list = []
        for _ in body:
            body_list.append(_.strip())
        body = '\n'.join(body_list)
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub(' +', ' ', body).strip()
        body = body.strip().strip('\n')
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        category = category.strip()
        return category, title, abstract, body

    def parse(self, response):
        url = response.request.url
        response.meta['lan_id'] = 2181
        # print(response.request.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('div.wrapper-news-art.col-md-6.col-sm-12')
        # print(block)
        if block is None or len(block) == 0:
            return
        # href_list = soup.select('h2.news-title > a')
        # size = len(href_list)
        # print(size)
        # while self.cnt1 < size:
        #     href = href_list[self.cnt1]['href']
        #     print(href)
        #     self.cnt1 += 1
        #     # print(self.cnt1)
        #     pattern = r"\d{4}-\d{2}-\d{2}"
        #     time_list = re.findall(pattern, href)[0]
        #     time_list = time_list.split('-')
        #     response.meta['pub_time'] = f'{time_list[0]}-{time_list[1]}-{time_list[2].zfill(2)} 00:00:00'
        #     if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(
        #             response.meta['pub_time']) < OldDateUtil.time:
        #         return
        #     yield scrapy.Request(url=href, callback=self.parse_item, meta=response.meta)
        for i in block:
            href = i.select_one('h2.news-title > a')['href']
            pattern = r"\d{4}-\d{2}-\d{2}"
            time_list = re.findall(pattern, href)[0]
            time_list = time_list.split('-')
            response.meta['pub_time'] = f'{time_list[0]}-{time_list[1]}-{time_list[2].zfill(2)} 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(
                    response.meta['pub_time']) < OldDateUtil.time:
                return
            # print(href)
            yield scrapy.Request(url=href, callback=self.parse_item, meta=response.meta)
        # 翻页操作：
        # 1. 不断增加页码数
        self.page += 1
        self.cnt1 = 0
        # 2. 拼接url
        url = url[0:url.rfind('/') + 1] + str(self.page)
        # print(url)
        # 3. 回调parse_page函数
        yield scrapy.Request(url=url, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        article = soup.select_one('div.article-body')
        body = ''.strip()
        for i in article.select('p'):
            body += i.text.replace('\n', '') + '\n'
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = soup.select_one(
            '#pcuba-news-article > div > section > nav > div.col-sm-12.wrapper-breadcrumb > ol > li.active').text
        item['title'] = soup.select_one(
            '#pcuba-news-article > div > section > article > div.col-sm-12 > h1').text
        item['language_id'] = response.meta['lan_id']
        img_list = article.select('img')
        img = []
        if img_list is not None:
            for i in img_list:
                if i['src'] != "":
                    if 'http' not in i['src']:
                        img.append('http://www.cuba.cu/' + i['src'])
                    else:
                        img.append(i['src'])
        item['images'] = img
        # print(img)
        item['category1'], item['title'], item['abstract'], item['body'] = \
            self.formalize(item['category1'], item['title'], None, body, item['language_id'])
        if item['body'] is not None and len(item['body']) > 2:
            # print(item)
            yield item
