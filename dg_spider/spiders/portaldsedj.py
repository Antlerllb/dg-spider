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


class PortaldsedjSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    name = 'portaldsedj'  # name的重命名
    language_id = 2122
    website_id = 2156  # id一定要填对！
    start_urls = ['https://portal.dsedj.gov.mo/webdsejspace/addon/msglistmainnews/MsgListMainNews2_main_page.jsp?prgvar'
                  '=MainNews2818104633246940508945&langsel=C&pageis=0',
                  'https://portal.dsedj.gov.mo/webdsejspace/addon/msglistmainnews/MsgListMainNews2_main_page.jsp?prgvar'
                  '=MainNews2818104633246940508945&langsel=E&pageis=0',
                  'https://portal.dsedj.gov.mo/webdsejspace/addon/msglistmainnews/MsgListMainNews2_main_page.jsp?prgvar'
                  '=MainNews2818104633246940508945&langsel=P&pageis=0']
    url1 = 'https://portal.dsedj.gov.mo/webdsejspace/addon/msglistmainnews/MsgListMainNews2_main_page.jsp?prgvar=' \
           'MainNews2818104633246940508945&langsel='
    url2 = '&pageis='
    m_pt = OldDateUtil.PT_2122_DATE
    m_en = OldDateUtil.EN_1866_DATE

    @staticmethod
    def remove_emoji(title, abstract, body):
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|"
            "[\U0001F700-\U0001F77F]|[\U0001F780-\U0001F7FF]|[\U0001F800-\U0001F8FF]|"
            "[\U0001F900-\U0001F9FF]|[\U0001FA00-\U0001FA6F]|[\U0001FA70-\U0001FAFF]|"
            "[\U00002702-\U000027B0]|[\U000024C2-\U0001F251]",
            flags=re.UNICODE)
        return emoji_pattern.sub('', title), emoji_pattern.sub('', abstract), emoji_pattern.sub('', body)

    @staticmethod
    def remove_invalid_utf8(text):
        pattern = re.compile(r'\\xF0\\xAA\\xB8\\xA9\\xE7\\x90')
        cleaned_text = re.sub(pattern, '', text)
        return cleaned_text

    @staticmethod
    def formalize(category, title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ').replace('\t', ' ').replace('\u3000', ' ').replace(' ', ' ').replace('\n', '')
        title = re.sub(' +', ' ', title).strip().strip('\n')
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
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        # print(body)
        # if language_id == 1813:
        #     category, title, abstract, body = convert(category, 'zh-cn'), convert(title, 'zh-cn'), \
        #                                       convert(abstract, 'zh-cn'), convert(body, 'zh-cn'),
        # print(body)
        # title, abstract, body = remove_emoji(title, abstract, body)
        # print(body)
        # title, abstract, body = OldFormatUtil.remove_invalid_utf8(title), OldFormatUtil.remove_invalid_utf8(
        #     abstract), OldFormatUtil.remove_invalid_utf8(body)
        return category, title, abstract, body

    def parse(self, response):
        url = response.request.url
        response.meta['page'] = 0
        if '&langsel=C' in url:
            response.meta['lan_id'] = 1813
            response.meta['category1'] = '新闻资讯'
        elif '&langsel=E' in url:
            response.meta['lan_id'] = 1866
            response.meta['category1'] = 'News'
        else:
            response.meta['lan_id'] = 2122
            response.meta['category1'] = 'Notícias'
        yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)

    def parse_pages(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        url_pre = response.request.url
        # print(url_pre)
        url_pre = url_pre[:url_pre.find('&pageis=') + 8]
        block = soup.select('div.listitem')
        if block is None or len(block) == 0:
            return
        for i in block:
            # break
            time_list = i.select_one('span.date1').text.replace('[', '').replace(']', '').split('-')
            response.meta['pub_time'] = f'{time_list[0]}-{time_list[1].zfill(2)}-{time_list[2].zfill(2)} 00:00:00'
            # print(response.meta['pub_time'])
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(response.meta['pub_time']) < OldDateUtil.time:
                return
            response.meta['title'] = i.select_one('a.link-mute').text.strip()
            href = 'https://portal.dsedj.gov.mo/webdsejspace/addon/allmain/msgfunc/Msg_funcmain_new_page.jsp?msg_id=' \
                   + i.select_one('a.link-mute')['href'].replace('/webdsejspace/addon/allmain/msgfunc'
                                                                 '/Msg_funclink_new_page.jsp?msg_id=', '')
            # href = 'https://portal.dsedj.gov.mo/webdsejspace/addon/allmain/msgfunc/Msg_funcmain_new_page.jsp?msg_id' \
            #        '=97982&langsel=C '
            # print(response.meta['title'])
            # print(href)
            yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)
            # return
        # 翻页操作：
        # 1. 不断增加页码数
        response.meta['page'] += 1
        # 2. 拼接url
        url = url_pre + str(response.meta['page'])
        # print(url)
        # 3. 回调parse_page函数
        yield scrapy.Request(url=url, callback=self.parse_pages, meta=response.meta)

    def parse_items(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(response.request.url)
        item = NewsItem(language_id=self.language_id)
        body = ''.strip()
        # for i in soup.select_one('div.col-sm-8').select('p'):
        #     body += i.text.replace('\n', '') + '\n'
        # print(soup)
        body = soup.select_one('div.main').text.strip()
        # print(body)
        # return
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['language_id'] = response.meta['lan_id']
        img_list = soup.select('img')
        img = []
        if img_list is not None:
            for i in img_list:
                image = i['src']
                if image is not None:
                    if 'https' in image:
                        img.append(image)
        item['images'] = img
        # print(img)
        item['category1'], item['title'], item['abstract'], item['body'] = \
            self.formalize(item['category1'], item['title'], None, body, item['language_id'])
        if item['body'] is not None and len(item['body']) > 2:
            # print(item)
            body = item['body'].strip()
            # print(body)
            # print(response.request.url)
            yield item
