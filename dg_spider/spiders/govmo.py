# encoding: utf-8
import datetime



from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import re
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import html
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil


# author : 张鸿兴
# 静态网站：内容与政府有关，新闻数据量较大，有图
# 通过parse函数获取第一页链接，parse_page函数使用bs4进行翻页，parse_items函数中使用bs4进行新闻爬取


class GovmoSpider(BaseSpider):  # 类名重命名
    author = "张鸿兴"
    name = 'govmo'  # name重命名，长度超过5个字符
    language_id = 2122  # 语言id
    website_id = 2168  # 网站id
    # id一定要填对！
    # 将不同语种对应的url放入起始列表中，进行异步爬取
    start_urls = ['https://www.gov.mo/zh-hans/news/page/1/?display_mode=list',
                  'https://www.gov.mo/en/news/page/1/?display_mode=list',
                  'https://www.gov.mo/pt/noticias/page/1/?display_mode=list']
    # now_year = int(str(datetime.datetime.now())[0:4])
    # 月份列表
    month_pt = OldDateUtil.PT_2122_DATE
    month_en = OldDateUtil.EN_1866_DATE

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
        abstract = re.sub('<[^>]+>', '', abstract)
        if len(body.split('\n')) == 1 and body != abstract:
            body = abstract + '\n' + body.strip()
        body = body.strip()
        return title, abstract, body

    def parse(self, response):
        # 获取链接
        url = response.request.url
        # print(url)
        # 判断语言
        if "pt" in url:
            response.meta['language_id'] = 2122  # 通过response.meta传参至下一个parse函数
        elif "zh-hans" in url:
            response.meta['language_id'] = 1813
        elif "en":
            response.meta['language_id'] = 1866
        response.meta['page'] = 1
        response.meta['url'] = url[0:url.find('/?')] + '/page/' + str(response.meta['page']) + '/?display_mode=list'
        # print(response.meta['url'])
        yield scrapy.Request(url=url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        # 配置解析器
        soup = BeautifulSoup(response.text, 'html.parser')
        # 选中一块块新闻（列表）
        block = soup.select('div.col-xs-12.content-block')
        # 遍历新闻块中的新闻
        for news in block:
            # 获取发布时间并与截止时间戳比较，决定是否爬取
            pub_time = news.select_one('time').text.strip()
            # print(pub_time)
            # 根据不同的语言修改月份为数字
            if response.meta['language_id'] == 2122:
                pub_time = pub_time.replace(' de', '')
                pub_time = pub_time[0:pub_time.find(' às')]
                time_list = pub_time.split(' ')
                # print(time_list)
                pub_time = f'{time_list[2]}-{str(self.month_pt[time_list[1]]).zfill(2)}-{time_list[0].zfill(2)} 00:00:00'
            elif response.meta['language_id'] == 1813:
                pub_time = pub_time[0:pub_time.find(' ')]
                time_list = re.split(r'年|月|日', pub_time)
                # print(time_list)
                pub_time = f'{time_list[0]}-{time_list[1].zfill(2)}-{time_list[2].zfill(2)} 00:00:00'
            elif response.meta['language_id'] == 1866:
                pub_time = pub_time.replace('th', '')
                pub_time = pub_time.replace('rd', '')
                pub_time = pub_time.replace('nd', '')
                if pub_time.find('1st') != -1:
                    pub_time = pub_time.replace('st', '', 1)
                pub_time = pub_time[0:pub_time.find(' at')].strip()
                time_list = pub_time.split(' ')
                # print(time_list)
                # print(time_list)
                pub_time = f'{time_list[2]}-{str(self.month_en[time_list[1]]).zfill(2)}-{time_list[0].zfill(2)} 00:00:00'
            response.meta['pub_time'] = pub_time
            # print(pub_time)
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            # 获取当前新闻链接
            href = news.select_one('h2 > a')['href']
            # print(href)
            # 进入parse_items函数以爬取新闻
            # href = 'https://www.gov.mo/zh-hans/news/700190/'
            # print(href)
            yield scrapy.Request(url=href, callback=self.parse_items, meta=response.meta)
            # break
        # 翻页操作：
        # 1. 不断增加页码数
        response.meta['page'] += 1
        # 2. 拼接url
        url = response.meta['url']
        url1 = url[0:url.find('page') + 5]
        url2 = url[url.find('/?'):url.find('list') + 4]
        url = url1 + str(response.meta['page']) + url2
        # print(url)
        # 3. 回调parse_page函数
        yield scrapy.Request(url=url, callback=self.parse_page, meta=response.meta)

    def parse_items(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        # 通过bs4的select和select_one获取信息
        pend_category = soup.select_one('aside.metadata-list').text.strip()  # strip()去除首尾空格
        # 根据语言修改category1这一信息
        if response.meta['language_id'] == 2122:
            if 'Categoria' in pend_category:
                item['category1'] = pend_category[pend_category.find('Categoria') + 11:]
            else:
                item['category1'] = 'Noticias'
        elif response.meta['language_id'] == 1813:
            if '类别' in pend_category:
                item['category1'] = pend_category[pend_category.find('类别') + 4:]
            else:
                item['category1'] = '新闻'
        elif response.meta['language_id'] == 1866:
            if 'Category' in pend_category:
                item['category1'] = pend_category[pend_category.find('Category') + 10:]
            else:
                item['category1'] = 'News'
        # print(item['category1'])
        # print(response.request.url)
        # 获取文章主体，修正最终文本格式，建议学习正则表达式有关内容
        article = soup.select_one('article')
        body_text = article.select('p')
        body = ""
        for text in body_text:
            body += text.text.strip()
            body += '\n'
        title = soup.select_one('div.news-title > h1').text.strip()
        title = title.replace('\r', ' ')
        title = title.replace('\t', ' ')
        title = title.replace('\u3000', ' ')
        item['pub_time'] = response.meta['pub_time']
        # 以列表的形式存储新闻图片
        # 爬虫运行后在数据库中运行以下命令检查是否存在格式不对的图片
        # SELECT * FROM news WHERE website_id = 2168 AND images != "[]" AND images not like "[\"http%";
        img_list = soup.select('figure.gallery-item')
        images = []
        for i in img_list:
            img = i.select_one('img')['src']
            if len(img) > 3:
                images.append(img[0:img.rfind('-')] + '.jpeg')
        # print(images)
        item['images'] = images
        item['language_id'] = response.meta['language_id']
        item['title'], item['abstract'], item['body'] = self.formalize(title, None, body, item['language_id'])
        # print(item['title'])
        # print(item)
        if len(item['body']) >= 5 and len(item['abstract']) >= 5:
            # pass
            yield item
        else:
            pass
