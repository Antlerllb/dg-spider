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


class AgenciabrasilSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    name = 'agenciabrasil'  # name的重命名
    language_id = 2122
    website_id = 680  # id一定要填对！
    start_urls = ['https://agenciabrasil.ebc.com.br/en/ultimas?page=1',
                  'https://agenciabrasil.ebc.com.br/ultimas?page=1',
                  'https://agenciabrasil.ebc.com.br/es/ultimas?page=1']
    url1 = 'https://agenciabrasil.ebc.com.br/'
    url2 = '?page='
    m_pt = OldDateUtil.PT_2122_DATE
    m_en = OldDateUtil.EN_1866_DATE
    m_sp = OldDateUtil.ES_2181_DATE

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
        title = re.sub(' +', ' ', title).strip().strip('\n')
        body = re.sub('<br>.*?<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub(' +', ' ', body).strip()
        body = AgenciabrasilSpider.remove_emoji(body)
        body = OldFormatUtil.remove_invalid_utf8(body)
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
        soup = BeautifulSoup(response.text, 'html.parser')
        url = response.request.url
        response.meta['page'] = 1
        # print(url)
        if "en/" in url:
            language_id = 1866
        elif "es/" in url:
            language_id = 2181
        else:
            language_id = 2122
        response.meta['url'] = url[0:url.find('/ultimas') + 8] + self.url2 + str(response.meta['page'])
        # print(response.meta['url'])
        response.meta['lan_id'] = language_id
        yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)

    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('div.row.my-4.d-flex')
        url_pre = response.request.url
        # print(url_pre)
        url_pre = url_pre[:url_pre.find('.br/') + 4]
        # print(block)
        if block is None or len(block) == 0:
            return
        for i in block:
            time_list = re.sub(r'\t', '',
                               i.select_one('div.post-meta.small.alt-font.font-italic.d-flex.flex-wrap').text.strip())
            time_list = re.sub('\n+', '\n', time_list)
            # print(time_list)
            time_list = time_list.split(',')[1].split('-')[0].strip().split('/')
            # print(time_list)
            # break
            response.meta['pub_time'] = f'{time_list[2]}-{time_list[1]}-{time_list[0].zfill(2)} 00:00:00'
            # print(response.meta['pub_time'])
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(response.meta['pub_time']) < OldDateUtil.time:
                return
            response.meta['category1'] = i.select_one('div.post-item-desc.py-0 > a > span').text.strip()
            response.meta['title'] = i.select_one('h4.alt-font.font-weight-bold.my-2').text
            # print(response.meta['category1'])
            # print(response.meta['title'])
            href = url_pre + i.select_one('div.post-item-desc.py-0 > a:nth-child(2)')['href']
            # href = 'https://agenciabrasil.ebc.com.br//es/esportes/noticia/2023-03/fluminense-enfrenta-volta-redonda
            # -en-la-apertura-de-la-semifinal-carioca'
            # print(href)
            yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)
        # 翻页操作：
        url = response.meta['url']
        # 1. 不断增加页码数
        response.meta['page'] += 1
        # 2. 拼接url
        # print(url)
        url1 = url[0:url.find('?page') + 6]
        url2 = ''
        url = url1 + str(response.meta['page'])
        # print(url)
        # 3. 回调parse_page函数
        yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)

    def parse_items(self, response):  # 主页，用于点进每个菜单
        # print(response.request.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        body = ''.strip()
        # for i in soup.select_one('div.col-sm-8').select('p'):
        #     body += i.text.replace('\n', '') + '\n'
        # print(body)
        body = soup.select_one('div.post-item-wrap')
        # print(body)
        if body is not None:
            body = body.text.strip()
            item['pub_time'] = response.meta['pub_time']
            item['category1'] = response.meta['category1']
            item['title'] = response.meta['title']
            item['language_id'] = response.meta['lan_id']
            img_list = soup.select_one('div.post-image > a > img')
            # print(img_list)
            img = []
            if img_list is not None:
                if img_list['data-echo'] != "":
                    image = img_list['data-echo']
                    # print(image)
                    if 'https://imagens.ebc.com.br/' in image:
                        image = image[image.find('https://agenciabrasil.ebc.com'):image.find('.jpg?') + 4]
                        if len(image) != 0:
                            img.append(image)
                    else:
                        pass
                else:
                    pass
            item['images'] = img
            # print(img)
            item['category1'], item['title'], item['abstract'], item['body'] = \
                self.formalize(item['category1'], item['title'], None, body, item['language_id'])
            # print(item['body'])
            if item['body'] is not None and len(item['body']) > 2:
                # pass
                # print(item)
                yield item
