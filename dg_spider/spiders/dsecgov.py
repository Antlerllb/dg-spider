# -*- coding: utf-8 -*-



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
# 动态网站，内容与统计有关，新闻数据量小（公示的新闻仅在LatestNews这一json文件中），无图
# 通过parse函数获取json以获取新闻id，再遍历，通过parse_items函数获取json进行新闻爬取
class DsecgovSpider(BaseSpider):  # 类名重命名，首字母大写
    author = "张鸿兴"
    name = 'dsecgov'  # name重命名，长度超过5个字符
    language_id = 2122  # 语言id
    website_id = 2162  # 网站id
    # id一定要填对！
    # 将不同语种对应的url放入起始列表中，进行异步爬取
    start_urls = ['https://www.dsec.gov.mo/StatisticsJSON/LatestNews_zh-MO.json?v=1.7.7&t=Ms4r%2f',
                  'https://www.dsec.gov.mo/StatisticsJSON/LatestNews_pt-PT.json?v=1.7.7&t=Ms4r%2f',
                  'https://www.dsec.gov.mo/StatisticsJSON/LatestNews_en-US.json?v=1.7.7&t=Ms4r%2f']
    # 遍历新闻时要给新闻id加上的链接前后缀
    # eg.'https://www.dsec.gov.mo/DSECAppApi/NewsAll/zh-MO/28820'
    url1 = "https://www.dsec.gov.mo/DSECAppApi/NewsAll/"
    url2 = ""  # 根据语言改变
    news_id = 0

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
        if "zh-MO" in url:
            response.meta['language_id'] = 1813  # 通过response.meta传参至下一个parse函数
            response.meta['category1'] = '新聞'
            self.url2 = "zh-MO/"
        elif "en-US" in url:
            response.meta['language_id'] = 1866
            response.meta['category1'] = 'News'
            self.url2 = "en-US/"
        elif "pt-PT" in url:
            response.meta['language_id'] = 2122
            response.meta['category1'] = 'Notícia'
            self.url2 = "pt-PT/"
        # 获取json
        res = response.json()
        # print(res)
        # 遍历新闻
        for i in res:
            self.news_id = i.get('ReleaseID')
            if self.news_id == 27026:
                pass
            elif self.news_id != 0:
                # 获取发布时间并与截止时间戳比较，决定是否爬取
                pub_time = i.get('NewsReleaseDate')
                time_list = pub_time[0:pub_time.find('T')].split('-')
                time = f'{time_list[0]}-{time_list[1]}-{time_list[2]} 00:00:00'
                response.meta['pub_time'] = time
                if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(time) < OldDateUtil.time:
                    return
                # 拼接新闻的链接
                url = self.url1 + self.url2 + str(self.news_id)
                # print(url)
            yield scrapy.Request(url=url, callback=self.parse_items, meta=response.meta)

    def parse_items(self, response):
        res = response.json()
        # print(res)
        item = NewsItem(language_id=self.language_id)
        # 通过json获取新闻信息
        title = res.get('Value').get('newsTitle').strip()
        item['category1'] = response.meta['category1']
        item['language_id'] = response.meta['language_id']
        body = res.get('Value').get('newsContent').strip()
        abstract = res.get('Value').get('newsAbstract').strip()
        item['title'], item['abstract'], item['body'] = self.formalize(title, abstract, body, item['language_id'])
        item['pub_time'] = response.meta['pub_time']
        # 本网站新闻无图片
        images = []
        # for i in img_list:
        #     images.append(i['src'])
        item['images'] = None
        yield item
