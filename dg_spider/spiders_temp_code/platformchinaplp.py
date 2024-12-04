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


class PlatformchinaplpSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    name = 'platformchinaplp'  # name的重命名
    language_id = 2122
    website_id = 2144  # id一定要填对！
    start_urls = ['https://www.platformchinaplp.mo/api/api//trade/get_list?keyword=&orderBy=&countryId'
                  '=&investmentIndustry=&cooperationType=&page=1&limit=20']
    url1 = 'https://www.platformchinaplp.mo/api/api//trade/get_list?keyword=&orderBy=&countryId=&investmentIndustry' \
           '=&cooperationType=&page='
    url2 = '&limit=20'
    page = 1
    m_pt = OldDateUtil.PT_2122_DATE
    m_en = OldDateUtil.EN_1866_DATE

    @staticmethod
    def formalize(category, title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ').replace('\n', '')
        title = re.sub(' +', ' ', title).strip().strip('\n')
        body = re.sub('<br>.*?<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = re.sub(' +', ' ', body).strip()
        body = body.strip().split('\n')
        body_list = []
        for _ in body:
            body_list.append(_.strip())
        body = '\n'.join(body_list)
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        if language_id == 1813:
            category, title, abstract, body = convert(category, 'zh-cn'), convert(title, 'zh-cn'), \
                                              convert(abstract, 'zh-cn'), convert(body, 'zh-cn'),
        return category, title, abstract, body

    def parse(self, response):
        res = response.json()
        block = res.get('data').get('list').get('records')
        item = NewsItem(language_id=self.language_id)
        if block is None or len(block) == 0:
            return
        for i in block:
            # break
            time_list = i.get('publishDate').split('-')
            item['pub_time'] = f'{time_list[0]}-{time_list[1].zfill(2)}-{time_list[2].zfill(2)} 00:00:00'
            # print(response.meta['pub_time'])
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(response.meta['pub_time']) < OldDateUtil.time:
                return
            if i.get('titlePt') is not None:
                item['language_id'] = 2122
                item['category1'] = 'Informações Económica-Comerciais'
                item['title'] = i.get('titlePt')
                body = i.get('descriptionPt')
                item['category1'], item['title'], item['abstract'], item['body'] = \
                    self.formalize(item['category1'], item['title'], None, body, item['language_id'])
                j = i.get('pic')
                img = []
                if j is not None:
                    if 'attachment' in j:
                        img.append('https://img.platformchinaplp.bringbuys.com/' + j)
                    else:
                        img.append('https://img.platformchinaplp.bringbuys.com/' + j[j.find('.com') + 4:])
                item['images'] = img
                if item['body'] is not None and len(item['body']) > 2:
                    yield item
            if i.get('titleZhs') is not None:
                item['language_id'] = 1813
                item['category1'] = '经贸资讯'
                item['title'] = i.get('titleZhs')
                body = i.get('descriptionZhs')
                item['category1'], item['title'], item['abstract'], item['body'] = \
                    self.formalize(item['category1'], item['title'], None, body, item['language_id'])
                j = i.get('pic')
                img = []
                if j is not None:
                    if 'attachment' in j:
                        img.append('https://img.platformchinaplp.bringbuys.com/' + j)
                    else:
                        img.append('https://img.platformchinaplp.bringbuys.com/' + j[j.find('.com') + 4:])
                item['images'] = img
                if item['body'] is not None and len(item['body']) > 2:
                    yield item
            if i.get('titleEn') is not None:
                item['language_id'] = 1866
                item['category1'] = 'Economic and Trade'
                item['title'] = i.get('titleEn')
                body = i.get('descriptionEn')
                item['category1'], item['title'], item['abstract'], item['body'] = \
                    self.formalize(item['category1'], item['title'], None, body, item['language_id'])
                j = i.get('pic')
                img = []
                if j is not None:
                    if 'attachment' in j:
                        img.append('https://img.platformchinaplp.bringbuys.com/' + j)
                    else:
                        img.append('https://img.platformchinaplp.bringbuys.com/' + j[j.find('.com') + 4:])
                item['images'] = img
                if item['body'] is not None and len(item['body']) > 2:
                    yield item
        # 翻页操作：
        # 1. 不断增加页码数
        self.page += 1
        # 2. 拼接url
        url = self.url1 + str(self.page) + self.url2
        # print(url)
        # 3. 回调parse_page函数
        yield scrapy.Request(url=url, callback=self.parse, meta=response.meta)
