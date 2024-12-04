import html
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.utils import spider




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
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re


class LarepublicaSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    name = 'larepublica'
    language_id = 2181
    website_id = 1306
    start_urls = ['https://larepublica.pe/api/search/articles?category_slug=&limit=20&page=1&order_by=update_date']
    url1 = 'https://larepublica.pe/api/search/articles?category_slug=&limit=20&page='
    url2 = '&order_by=update_date'
    page = 1
    m_pt = OldDateUtil.PT_2122_DATE
    m_en = OldDateUtil.EN_1866_DATE

    @staticmethod
    def is_only_symbols(string):
        pattern = r'^[^\w\s]+$'  # 匹配只包含符号的模式
        match = re.match(pattern, str(string))
        return match is not None

    @staticmethod
    def remove_emoji(text):
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|"
            "[\U0001F700-\U0001F77F]|[\U0001F780-\U0001F7FF]|[\U0001F800-\U0001F8FF]|"
            "[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FA6F]|[\U0001FA70-\U0001FAFF]|"
            "[\U00002702-\U000027B0]|[\U000024C2-\U0001F251]",
            flags=re.UNICODE)
        return emoji_pattern.sub('', text)

    @staticmethod
    def formalize(category, title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ').replace('\n', '')
        title = re.sub(' +', ' ', title).strip().strip('\n').replace('\n', '')
        body = re.sub('<br>.*?<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
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
        body = LarepublicaSpider.remove_emoji(body)
        
        title = OldFormatUtil.remove_invalid_utf8(title)
        body = OldFormatUtil.remove_invalid_utf8(body)
        body = re.sub(' +', ' ', body).strip()
        body = body.strip().strip('\n')
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        if language_id == 1813:
            category, title, abstract, body = convert(category, 'zh-cn'), convert(title, 'zh-cn'), \
                                              convert(abstract, 'zh-cn'), convert(body, 'zh-cn'),
        return category, title, abstract, body

    def parse(self, response):
        res = response.json()
        block = res.get('articles').get('data')
        for i in block:
            time_list = i.get('date').split(' ')[0].split('-')
            response.meta['pub_time'] = f'{time_list[0]}-{time_list[1].zfill(2)}-{time_list[2].zfill(2)} 00:00:00'
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(response.meta['pub_time']) < OldDateUtil.time:
                return
            if i.get('title') is not None:
                response.meta['title'] = i.get('title')
                # print(response.meta['title'])
                data = i.get('data')
                if data is not None:
                    cate = data.get('categories')
                    if cate is not None:
                        response.meta['category1'] = cate[-1].get('name')
                        # print(response.meta['category1'])
                        href = 'https://larepublica.pe' + i.get('slug')
                        # print(href)
                        yield scrapy.Request(url=href, callback=self.parse_item, meta=response.meta)
                        # return
        # 翻页操作：
        # 1. 不断增加页码数
        self.page += 1
        if self.page <= 5000:
            # 2. 拼接url
            url = self.url1 + str(self.page) + self.url2
            # print(url)
            # 3. 回调parse_page函数
            yield scrapy.Request(url=url, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        # print(response)
        # print(response.text)
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        # return
        article = soup.select_one('div.MainContent_main__body__i6gEa')
        if article is None:
            article = soup.select_one('div.MainContentVerificador_content__notice__verificador__2LvaP')
        if article is not None:
            # print(article)
            article = article.select('p')
            # print(article)
            # return
            body = ''
            for i in article:
                body += i.text.strip().replace('\n', '') + '\n'
            item['pub_time'] = response.meta['pub_time']
            item['language_id'] = self.language_id
            item['category1'] = response.meta['category1']
            item['title'] = response.meta['title']
            item['category1'], item['title'], item['abstract'], item['body'] = \
                self.formalize(item['category1'], item['title'], None, body, item['language_id'])
            img = []
            pic = soup.select_one('picture > img')
            if pic is not None:
                if 'http' in pic['src']:
                    img.append(pic['src'])
                else:
                    img.append('http:' + pic['src'])
            images = soup.select('div.content_img')
            if images is not None and len(images) > 0:
                for j in images:
                    image = j.select_one('img')
                    if image['src'] is not None:
                        if 'http' in image['src']:
                            img.append(image['src'])
                        else:
                            img.append('http:' + image['src'])
            item['images'] = img
            if item['body'] is not None and len(item['body']) > 2:
                yield item
