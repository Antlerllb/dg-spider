
# 此文件包含的头文件不要修改
import scrapy
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
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
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http import Request, Response
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import requests
from datetime import datetime
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import socket

#将爬虫类名和name字段改成对应的网站名
class inextliveSpider(BaseSpider):
    name = 'inextlive'
    website_id = 1127 # 网站的id(必填)
    language_id = 1866 # 所用语言的id
    start_urls = ['https://www.inextlive.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_admin',
        'password': 'dg_admin',
        'db': 'dg_crawler'
    }

    # 这是类初始化函数，用来传时间戳参数
    
         
        

    def parse(self,response):# 进入一级目录
        html = BeautifulSoup(response.text)
        for i in html.select('#mainNav a')[2:14]:
            yield Request(i.attrs['href'],callback=self.parse2)

    def parse2(self,response):
        socket.setdefaulttimeout(30)
        html = BeautifulSoup(response.text)
        if len(html.select('.topicList')):# 若有新闻列表则分析
            for i in html.select('.topicList a'):
                yield Request(i.attrs['href'],callback=self.parse3)# 返回每条新闻于parse3
            timelist = re.findall(r'\| Updated Date: \S+, (\d+ \S+ \d+ \d+:\d+:\d+)',requests.get(html.select('.topicList a')[-1].attrs['href']).text)[0].split(' ')
            time_ = time.strftime("%Y-%m-%d ",datetime(int(timelist[2]),OldDateUtil.month[timelist[1]],int(timelist[0])).timetuple()) + timelist[3]# 拿取最后一条新闻的时间
            if OldDateUtil.time == None or OldDateUtil.format_time3(time_) >= int(OldDateUtil.time):# 截止功能
                if len(html.select('.pagination.border0 .last a')):
                    yield Request(html.select('.pagination.border0 .last a')[0].attrs['href'],callback=self.parse2)
                else:
                    for i in html.select('.pagination.border0 a'):
                        yield Request(i.attrs['href'],callback=self.parse2)
        else:# 若有多级目录则进入
            if len(html.select('.MainHd a')):
                for i in html.select('.MainHd a'):
                    yield Request(i.attrs['href'],callback=self.parse2)

    def parse3(self,response):# 分析网页挖取数据
        html = BeautifulSoup(response.text)
        item = NewsItem(language_id=self.language_id)
        item['title'] = html.select('.topHeading h1')[0].text
        item['category1'] = html.select('.breadcrum .first span')[0].text
        item['category2'] = html.select('.breadcrum span')[-2].text if len(html.select('.breadcrum span')) >= 4 else None
        item['body'] = ''
        for i in html.select('.articleBody p'):
            item['body'] += (i.text+'\n')
        if html.select('.articleBody p') != []:
            item['abstract'] = html.select('.articleBody p')[0].text
        timelist = re.findall(r'\| Updated Date: \S+, (\d+ \S+ \d+ \d+:\d+:\d+)',response.text)[0].split(' ')
        item['pub_time'] = time.strftime("%Y-%m-%d ",datetime(int(timelist[2]),OldDateUtil.month[timelist[1]],int(timelist[0])).timetuple()) + timelist[3]
        if html.select('.bodySummery img') != []:
            item['images'] = [html.select('.bodySummery img')[0].attrs['data-src'],]
        yield item