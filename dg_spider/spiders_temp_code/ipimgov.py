# encoding: utf-8
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.utils import spider




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
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re
import html
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


# author : 张鸿兴
class IpimgovSpider(BaseSpider):  # 类名重命名
    author = "张鸿兴"
    name = 'ipimgov'  # name的重命名
    language_id = 2122
    website_id = 2174  # id一定要填对！
    allowed_domains = ['ipim.gov.mo']
    start_urls = ['https://www.ipim.gov.mo/zh-hans/page/1/?s', 'https://www.ipim.gov.mo/pt-pt/page/1/?s',
                  'https://www.ipim.gov.mo/en/page/1/?s']
    # start_urls = ['https://www.ipim.gov.mo/zh-hans/page/98/?s']
    f = 0
    page = 1

    @staticmethod
    def formalize(title, abstract, body, language_id):
        title = re.sub('\n+', '', title).strip('\n')
        title = title.replace('\r', ' ')
        title = title.replace('\t', ' ')
        title = title.replace('\u3000', ' ')
        title = title.replace(' ', ' ')
        title = title.replace('\n', '')
        title = re.sub(' +', ' ', title)
        title = title.strip().strip('\n')
        body = re.sub('<br>　　<br>', '\n', body)
        body = re.sub('\n+', '\n', body.strip()).strip('\n')
        body = html.unescape(body)  # 将html中的转义字符解码
        body = re.sub('<[^>]+>', '', body)
        body = body.replace('\r', ' ')
        body = body.replace('\t', ' ')
        body = body.replace('\u3000', ' ')
        body = body.replace(' ', ' ')
        body = re.sub(' \n', '', body).strip('\n')
        body = re.sub(' +', ' ', body)
        body = body.strip()
        if language_id == 1813:
            body = convert(body, 'zh-cn')
        if abstract is None:
            abstract = re.sub('\n+', '\n', body.split('\n')[0]).strip('\n')
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        return title, abstract, body

    def parse(self, response):  # 第一页
        url = response.request.url
        response.meta['page'] = 1
        yield scrapy.Request(url=url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):  # 新闻列表页，用于点进每个新闻
        # print(response.request.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        block = soup.select('.component-view>ul>li>div>h4>a')
        # print(block)
        first_time = 0
        for i in range(0, len(block)):
            if '1267/1989/2253' in block[i].text or '/DSO/IPIM/' in block[i].text:
                pass
            else:
                title_split = re.split(r'[ \[\]]', block[i].text)
                # print(title_split)
                for j in range(0, len(title_split)):
                    if '/' in title_split[j] or '-' in title_split[j]:
                        title = title_split[j]
                        # print(title)
                        if len(title) >= 2:
                            time_list = re.split(r'[-/]', title)
                            # print(time_list)
                            if time_list[0].isdigit() and len(time_list) >= 3:
                                pub_time = f'{time_list[0]}-{time_list[1]}-{time_list[2]} 00:00:00'  # '2022-10-11 00:00:00'
                                # print(pub_time)
                                pub_time = OldDateUtil.str_datetime_to_timestamp(pub_time)
                                # print(pub_time)
                                first_time = max(first_time, int(pub_time))
        # print(OldDateUtil.time_stamp2formate_time(first_time))
        if first_time != 0:
            # print(first_time)
            if OldDateUtil.time is not None and first_time < OldDateUtil.time:
                # print("first out of time", str(self.page))
                return
            for i in range(0, len(block)):
                title_split = re.split(r'[ \[\]]', block[i].text)
                for j in range(0, len(title_split)):
                    if '/' in title_split[j] or '-' in title_split[j]:
                        title = title_split[j]
                        break
                # print(title)
                if len(title) >= 2:
                    time_list = re.split(r'[-/]', title)
                    # print(time_list)
                    if time_list[0].isdigit() and len(time_list) >= 3:
                        pub_time = f'{time_list[0]}-{time_list[1]}-{time_list[2]} 00:00:00'  # '2022-10-11 00:00:00'
                        response.meta['pub_time'] = pub_time
                        pub_time = OldDateUtil.str_datetime_to_timestamp(pub_time)
                        if OldDateUtil.time is not None and pub_time < OldDateUtil.time:
                            self.f = 1
                            # print("pub out of time", str(self.page))
                            pass
                        else:
                            abstract = block[i].parent.parent.find('p')
                            # print(abstract)
                            if abstract is not None:
                                response.meta['abstract'] = abstract.text.strip()
                            else:
                                response.meta['abstract'] = " "
                            if 'pdf' not in block[i]['href'] and '/services/' not in block[i]['href']:
                                href = block[i]['href']
                                # href = 'https://www.ipim.gov.mo/' + href
                                # print(href)
                                pend_language = href[0:33]
                                if "pt-pt" in pend_language:
                                    response.meta['language_id'] = 2122
                                elif "en" in pend_language:
                                    response.meta['language_id'] = 1866
                                elif "zh-hans" in pend_language:
                                    response.meta['language_id'] = 1813
                                if 'ipim.gov.mo/' in href and 'service-booking-form' not in href and \
                                        'publication' not in href and 'promotional-video-sc' not in href and \
                                        'member' not in href and \
                                        'temporary-residency-online-appointment-notice' not in href and \
                                        'investment-environment' not in href and \
                                        'bm.ipim.gov.mo/index.html' not in href and \
                                        '/ghmetcip/' not in href and \
                                        'investhere.ipim' not in href and \
                                        href != "https://www.ipim.gov.mo/pt-pt/":
                                    # pass
                                    yield Request(href, callback=self.parse_item, meta=response.meta)
        url = response.request.url
        url1 = url[0:url.find('page/') + 5]
        # print(url1)
        url2 = '/?s'
        response.meta['page'] += 1
        end_pages = int(soup.select('.page-numbers')[-2].text)
        # print(pages)
        url = url1 + str(response.meta['page']) + url2
        response.meta['url'] = url
        # print(url)
        if response.meta['page'] <= end_pages:
            yield scrapy.Request(url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):  # 爬取新闻信息
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        category1 = soup.select_one(
            '#main > div.component-view.component-page-toolbar > div > div.component-view.component-breadcrumbs > div '
            '> a:nth-child(3)')
        if category1 is not None:
            item['category1'] = category1.text
            # print(item['category1'])
        else:
            item['category1'] = "---"
        title = soup.select_one('h1')
        if title is not None:
            # item['title'] = title.text.strip()[13:]
            title = title.text.strip()[title.text.strip().find(']') + 2:]
            # print(item['title'])
        if title is None or len(title) <= 1:
            title = "---"
        item['pub_time'] = response.meta['pub_time']
        # print(item['pub_time'])
        img_list = soup.select_one('#main > div.component-view.component-content')
        if img_list is not None:
            img_list = img_list.select('img')
            img_list = [img.get('src') for img in img_list]
        else:
            img_list = []
        if len(img_list) >= 1:
            for img in range(0, len(img_list)):
                if 'http' not in img_list[img]:
                    img_list[img] = "https://www.ipim.gov.mo" + img_list[img]
        item['images'] = img_list
        # print(img_list)
        if soup.select_one('.component-content') is not None:
            body = '\n'.join(
                i.strip() for i in soup.select_one('.component-content').text.split('\n') if
                i.strip() != '')
        abstract = response.meta['abstract']
        if len(abstract) < 3:
            abstract = None
        # print(item)
        item['language_id'] = response.meta['language_id']
        if body is not None and len(body) > 1:
            item['title'], item['abstract'], item['body'] = self.formalize(title, abstract, body, item['language_id'])
            yield item
        # 不报错时要检查数据库
