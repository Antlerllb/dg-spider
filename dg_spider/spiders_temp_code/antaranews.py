# encoding: utf-8
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



import datetime
from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
Month = {'Januari': '01',
         'Februari': '02',
         'Maret': '03',
         'April': "04",
         'Mei': '05',
        'Juni': '06',
        'Juli': '07',
        'Agustus': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Desember': '12'} # 印尼语月份

#author: 蔡卓妍
def p_time(pt):
    if 'hour' in pt:
        t = pt.split()
        p_t = OldDateUtil.get_time_ago_stamp(hour=int(t[0]))
        l_time = OldDateUtil.timestamp_to_datetime_str(p_t)
    elif 'minutes' in pt:
        t = pt.split()
        p_t = OldDateUtil.get_time_ago_stamp(minute=int(t[0]))
        l_time = OldDateUtil.timestamp_to_datetime_str(p_t)
    elif 'menit' in pt:
        t = pt.split()
        p_t = OldDateUtil.get_time_ago_stamp(minute = int(t[0]))
        l_time = OldDateUtil.timestamp_to_datetime_str(p_t)
    else:
        try: # 英语版
            if 'nd' in pt:
                l_time = datetime.datetime.strptime(pt, '%dnd %B %Y')
            elif 'th' in pt:
                l_time = datetime.datetime.strptime(pt, '%dth %B %Y')
            elif 'rd' in pt:
                l_time = datetime.datetime.strptime(pt, '%drd %B %Y')
            else:
                l_time = datetime.datetime.strptime(pt, '%dst %B %Y')
        except: # 印尼版
            try:
                p_t = pt.split(',')[1].strip().split()
                if len(p_t[0]) < 2:
                    p_t[0] = '0' + p_t[0]
                l_time = p_t[2] + '-' + Month[p_t[1]] + '-' + p_t[0] + ' ' + p_t[3] + ':00'
            except:
                p_t = pt.strip().split()
                if len(p_t[0]) < 2:
                    p_t[0] = '0' + p_t[0]
                l_time = p_t[2] + '-' + Month[p_t[1]] + '-' + p_t[0] + ' ' + p_t[3] + ':00'
    return l_time

class AntaranewsSpider(BaseSpider):
    name = 'antaranews'
    website_id = 371
    # language_id = 1866 #1952 有英文和印尼两个版本(item传入
    start_urls = ['https://en.antaranews.com/', #英文版
                  'https://www.antaranews.com/'] #印尼版
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if 'en' in response.url:
            lists = soup.find_all(role="button")[1:-1]
        else:
            lists = soup.find_all(role="button")[1:12] #剩下内容与这一些是重复的
        for i in lists:
            nurl = i.get('href')
            category1 = i.text
            yield Request(url=nurl,callback=self.parse_page,meta={'category1':category1})

    def parse_page(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            flag = True
            OldDateUtil.time = OldDateUtil.str_datetime_to_timestamp('2022-01-01 00:00:00')
            ltime = soup.select("div.col-md-8 article span")[-1].text.strip()
            last_time = p_time(ltime)
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
                lists = soup.select("article.simple-post.simple-big.clearfix > header > h3 > a")
                for i in lists:
                    response.meta['title'] = i.text
                    news_url = i['href']
                    yield Request(url=news_url, callback=self.parser_item,meta=response.meta)
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:
                next_page = soup.select("ul.pagination.pagination-sm li")[-1].select_one("a").get("href")
                yield Request(url=next_page, callback=self.parse_page,meta=response.meta)
        except: #有一个不是新闻
            pass

    def parser_item(self,response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        try:
            item['body'] = "\n".join(i.text.strip() for i in soup.select("div.post-content.clearfix"))
            item['abstract'] = soup.select_one("div.post-content.clearfix").text.strip()
        except:
            item['body'] = "\n".join(i.text.strip() for i in soup.select(".flex-caption"))
            item['abstract'] = soup.select_one(".flex-caption").text.strip()
        ptime = soup.select_one('.article-date').text.strip()
        item['pub_time'] = p_time(ptime)
        try:
            if soup.select_one("header.post-header.clearfix img").get('src') != None:
                item['images'] = [i.get('src') for i in soup.select("header.post-header.clearfix img")]
            else:
                item['images'] = [i.get('data-src') for i in soup.select("header > figure > picture > img")]
        except:
            item['images'] = [i.get('src') for i in soup.select(".post-wrapper.clearfix img")]
        if '//en' in response.url:
            item['language_id'] = 1866
        else:
            item['language_id'] = 1952
        yield item