# encoding: utf-8
import html
import json
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
from scrapy.http.request.form import FormRequest
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


# Author:陈卓玮
# check: 凌敏 pass
class pelita_spider(BaseSpider):
    name = 'pelita'
    website_id = 220
    language_id = 2036
    start_urls = ['https://www.pelitabrunei.gov.bn/Lists/Berita%202018/AllBerita_2018.aspx']

    def parse(self,response):##发起post请求 循环翻页 获取列表 / 发起详情页请请求
        soup = BeautifulSoup(response.text, 'lxml')
        list = soup.select('#WebPartWPQ2 table tr')[0:-1]
        e_list = []
        item_time=OldDateUtil.get_now_datetime_str()
        for i in list:
            if (i.select_one('#group0 .ms-gb')) != None:
                item_time = i.select_one('#group0 .ms-gb').text.split('-')
                item_time[0], item_time[-1] = item_time[-1], item_time[0]
                item_time = '-'.join(item_time)+" 00:00:00"
            elif len(e_list) == 0 or i.select_one('h4').text != e_list[-1]['title']:
                e_list.append({'title': i.select_one('h4').text,
                               'url': i.select_one('a').get('href'),
                               'time': item_time})
        for i in e_list:
            yield Request(url="https://www.pelitabrunei.gov.bn/"+i['url'],
                          callback=self.__parse_essay,
                          meta={'title': i['title'],'time': i['time']},
                          dont_filter=True,)

        n_payload = eval(soup.select('.ms-paging > a')[-1].get('href').split("__doPostBack")[-1].replace(";", ''))
        n_payload = {'__EVENTTARGET': n_payload[0],
                     '__EVENTARGUMENT': n_payload[1].replace("dvt_start",";dvt_start")}
        # print(n_payload)
        if OldDateUtil.time==None or OldDateUtil.time <= OldDateUtil.str_datetime_to_timestamp(item_time):
            yield FormRequest(url = self.start_urls[0],
                              method='POST',
                              formdata=n_payload,
                              callback=self.parse,
                              dont_filter=True,
                              headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})

    def __parse_essay(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        body = '\n'.join(i.text.strip() for i in soup.select('.container p'))[1:].replace("​",'')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['category1'] = "News"
        item['body'] = body
        for i in soup.select('.container p'):
            if len(i.text)>6:
                item['abstract'] = i.text
        item['pub_time'] = response.meta['time']
        item['images'] = list("https://www.pelitabrunei.gov.bn" + i.get('src') for i in soup.select('img'))
        yield item