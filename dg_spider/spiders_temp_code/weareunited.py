from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import datetime
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re


time_dict={'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08',
           'September':'09','October':'10','November':'11','December':12}


def convert_time(time_text):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    time_list = re.split(r'[,:\'\s]\s*', time_text)  # %Y-%m-%d %H:%M:%S
    try:
        if 'ago' in time_text:
            unit = time_list[1]
            number = time_list[0]
            if unit =='hours':
                pub_time = (current_time + datetime.timedelta(hours=int(number))).strftime("%Y-%m-%d %H:%M:%S")
            elif unit == 'mins':
                pub_time = (current_time + datetime.timedelta(minutes=int(number))).strftime("%Y-%m-%d %H:%M:%S")

            else:
                pub_time = (current_time + datetime.timedelta(seconds=int(number))).strftime("%Y-%m-%d %H:%M:%S")

        else:
            pub_time = '{}-{}-{} {}:{}:{}'.format(time_list[2],time_dict[time_list[1]],time_list[0],'00','00','00')
    except:
        pub_time = current_time
    return pub_time

# author : 华上瑛

class WeareunitedSpider(BaseSpider):
    name = 'weareunited'
    website_id = 163
    language_id = 2266
    start_urls = ['https://weareunited.com.my/sort/latest/','https://weareunited.com.my/sort/breaking-news/',
                  'https://weareunited.com.my/sort/popular/','https://weareunited.com.my/sort/featured/',
                  'https://weareunited.com.my/tag/advertisement/']
    # is_http = 1
    #若网站使用的是http协议，需要加上这个类成员(类变量)
    # proxy = '02' #这个网站会反爬

    def start_requests(self):
        for i in self.start_urls:
            yield Request(url=i,callback=self.parse_page)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        articles = soup.select('div.row.gridlove-posts > div.col-lg-4.col-md-6.col-sm-12.layout-simple > article')
        if OldDateUtil.time is not None:
            last_time = convert_time(articles[-1].select('div > div > span.updated')[0].text)
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                article_url = article.select('div.box-inner-p > div > h2 > a')[0].get('href')
                image = [article.select('div.entry-image > a > img')[0].get('src')]
                title = article.select('div.box-inner-p > div > h2 > a')[0].text
                try:
                    category1 = article.select('div.entry-image > div > a')[0].text
                except:
                    category1 = response.url.split('/')[4]
                pub_time = convert_time(article.select('div > div > span.updated')[0].text)
                yield Request(url=article_url, callback=self.parse_item, meta={'category1':category1,'title': title,
                                                                               'images':image,'pub_time':pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            try:
                if response.url.split('/')[-2].isdigit():
                    url_list = response.url.split('/')
                    url_list[-2] = str(int(response.url.split('/')[-2])+1)
                    next_page = '/'.join(url_list)
                else:
                    next_page = response.url + 'page/2/'
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
            except:
                self.logger.info(response.url + ' has no the next page.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        content = soup.select('div.single_para.test > p')
        body = " "
        for b in content:
            body += b.text.strip()
        abstract = body.split('。')[0]

        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['body'] = body
        item['abstract'] = abstract
        item['images'] = response.meta['images']
        item['pub_time'] = response.meta['pub_time']
        yield item


