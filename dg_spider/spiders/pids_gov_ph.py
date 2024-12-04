import socket

import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# 此文件包含的头文件不要修改

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http import Request, Response
from zhconv import convert
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

# author:魏芃枫


class Pids(BaseSpider):
    name = 'pids_gov_ph'
    start_urls = [f'https://pids.gov.ph/press-releases?year={str(i)}' for i in range(2013, 2022)]
    website_id = 699 # 网站的id(必填)
    language_id = 1866  # 所用语言的id

    def parse(self, response):  # 获取不同年份下的不同页
        head_url = response.url
        soup = BeautifulSoup(response.text, 'html.parser')
        page_list = soup.select(".paginate-wrapper>ul>li")
        page_num = int(len(page_list) / 2 - 4) # 根据li标签数量计算得页数
        for j in range(1, page_num+1):
            url = head_url+"&pagenum="+str(j)
            yield Request(url, callback=self.parse_page)

    def parse_page(self, response):
        socket.setdefaulttimeout(30)
        soup = BeautifulSoup(response.text, 'html.parser')
        menu = soup.find_all(attrs={'class': "row column content-list arrow-button with-icon"})
        for i in menu:
            try:
                title = i.select_one("h4").text
                date = i.select_one('p').text.split(" ")
                month = str(OldDateUtil.EN_1866_DATE[date[1]]).zfill(2)
                day = date[2].replace(',', "")
                year = date[3]
                pub_time = str(year) + "-" + str(month) + "-" + str(day) + " 00:00:00"
                timestamp = OldDateUtil.str_datetime_to_timestamp(pub_time)
                if OldDateUtil.time == None or timestamp >= int(OldDateUtil.time):
                    href = "https://pids.gov.ph"+i.select_one("a").get('href')
                    meta = {'title': title, 'pub_time': pub_time}
                    yield Request(href, callback=self.parse_detail, meta=meta)
                else:
                    break  #  时间截止了，就退出循环。
                    self.logger.info('时间截止！')
            except:
                continue

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['body'] = soup.find(attrs={"class": 'large-8 columns page-content-column'}).text.strip()
        item['abstract'] = soup.find(attrs={"class": 'large-8 columns page-content-column'}).text.split('\n')[0]
        item['category1'] = None
        item['category2'] = None
        item['images'] = None
        yield item