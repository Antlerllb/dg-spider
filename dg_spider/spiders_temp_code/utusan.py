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

import re

# author : 林泽佳
time_dict = {'Januari': '01', 'Februari': '02', 'Mac': '03', 'April': '04', 'Mei': '05', 'Jun': '06', 'Julai': '07',
             'Ogos': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Disember': '12', 'pm': 12, 'am': 0}


class UtusanSpider(BaseSpider):
    name = 'utusan'
    website_id = 158
    language_id = 2036
    start_urls = ['http://www.utusan.com.my/'] #http://www.utusan.com.my/
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD': "TLSv1.2", 'PROXY': "02"}
    # proxy = '02'

    def parse(self, response):#初始页面，解析列表和其他数据
        soup = BeautifulSoup(response.text, 'lxml')
        navigation = soup.find_all("ul", id="menu-1-27a4dad5")[0]
        for nav in navigation:
            if nav != '\n':
                sub_menu = nav.select('li > ul')
                if len(sub_menu) != 0:
                    sub_categorys = nav.select('li > ul')[0].select('li > a')
                    for sub_category in sub_categorys:
                        sub_href = sub_category.get('href')
                        yield Request(url=sub_href, callback=self.parse_page, meta={'category1':sub_href.split('/')[-3],'category2':sub_href.split('/')[-2]})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.jeg_posts_wrap > div > article')
        if OldDateUtil.time is not None:
            last_time_ = articles[-1].select('div > div > div > a')[0].text.strip()
            time_list = re.split(r'[,:\'\s]\s*', last_time_)  # %Y-%m-%d %H:%M:%S
            if int(time_list[3]) == 12:
                hh = int(time_list[3])
            else:
                hh = str(int(time_list[3]) + time_dict[time_list[-1]])
            last_time = "{}-{}-{} {}:{}:{}".format(time_list[2], time_dict[time_list[1]], time_list[0], hh,
                                                  time_list[-2], "00")
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                time = article.select('div > div > div > a')[0].text.strip()
                time_list = re.split(r'[,:\'\s]\s*', time)  # %Y-%m-%d %H:%M:%S
                if int(time_list[3]) == 12:
                    hh = int(time_list[3])
                else:
                    hh = str(int(time_list[3]) + time_dict[time_list[-1]])
                pub_time = "{}-{}-{} {}:{}:{}".format(time_list[2], time_dict[time_list[1]], time_list[0], hh,
                                                       time_list[-2], "00")

                href = article.select('div > div > div > a')[0].get('href')
                yield Request(url=href, callback=self.parse_item, meta={'pub_time':pub_time,'category1':response.meta['category1'],'category2':response.meta['category2']})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            try:
                soup.select('span.page_info')[0].text.split(' ')[-1]
            except:
                self.logger.info("no more pages")
            else:
                whole_pages = soup.select('span.page_info')[0].text.split(' ')[-1]
                page_mark = response.url.split('/')[-2]
                if page_mark.isdigit() and int(page_mark) >= int(whole_pages):
                    self.logger.info("no more pages")
                elif page_mark.isdigit():
                    next_page_link_list = response.url.split('/')
                    next_page_link_list[-2] = str(int(page_mark)+1)
                    next_page_link = '/'.join(next_page_link_list)
                    yield Request(url=next_page_link, callback=self.parse_page, meta=response.meta)
                else:
                    next_page_link = response.url + 'page/2/'
                    yield Request(url=next_page_link, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):#点进文章里面的内容
        soup = BeautifulSoup(response.text, 'lxml')
        article = soup.find_all("div", id="content")[0]
        title = soup.select('div.elementor-widget-container > h1')[0].text
        img = [soup.select('div.elementor-image > figure > img')[0].get('src')]
        body_list = article.select("div.elementor-widget-container > div > p")
        if len(body_list) == 0:
            body_list = article.select("div.elementor-widget-container > p")
        body_list2 = []
        for b in body_list:
            body_list2.append(b.text.strip())
        body = " ".join(body_list2)
        abstract = body.split('.')[0]

        item = NewsItem(language_id=self.language_id)
        item['title'] = title # response.meta['title']
        item['abstract'] = abstract # response.meta['abstract']
        item['body'] = body # response.mata['body']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['images'] = img  # response.meta['category2']

        yield item
