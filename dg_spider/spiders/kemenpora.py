# -*- codeing = utf-8 -*-
# @Time : 2022/7/26 10:21
# @Author : 肖梓俊
# @File : kemenpora.py
# @software: PyCharm




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

month = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'Mai': '05',
        'Mei': '05',
        'Jun': '06',
        'Jul': '07',
        'Agst': '08',
        'Ags': '08',
        'Sep': '09',
        'Okt': '10',
        'Nov': '11',
        'Des': '12',
    } # 印尼语时间(简写版

# author : 肖梓俊
# check:why
class kemenporaSpider(BaseSpider):
    name = 'kemenpora'
    website_id = 107
    language_id = 1952
    start_urls = ['https://www.kemenpora.go.id/berita',
                  'https://www.kemenpora.go.id/inspirasi']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        category1 = soup.select_one('.mainwrap > main .hlm-title span .strong').text
        for i in soup.select('.newsrow .newsrow__row')[:15]: # 只有前15条是该类的新闻 后面5条是另外一类 且内容重复
            t = i.select_one('.catedate .date').text.strip().split(' ')
            t = t[3] + '-' + month[t[2]] + '-' + t[1] + " 00:00:00"
            title = i.select_one('h2').text
            url = i.select_one('a').get('href')
            meta = {
                'title': title,
                'time': t,
                'category1' : category1
            }
            yield Request(url=url, callback=self.parse_item, meta=meta)
        t = soup.select('.catedate .date')[14].text.strip().split()
        # print(soup.select('.catedate .date')[14].text.strip().split())
        last_time = t[3] + '-' + month[t[2]] + '-' + t[1] + " 00:00:00"
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            try: # 翻页
                url = soup.find(rel='next')['href']
                # print(url)
                yield Request(url=url,callback=self.parse)
            except:
                self.logger.info("no more pages")

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        meta = response.meta
        item['category1'] = meta['category1']
        item['title'] = meta['title']
        item['pub_time'] = meta['time']
        item['body'] = '\n'.join([paragraph.strip() for paragraph in
                                  ["".join(text.xpath('.//text()').getall()) for text in response.xpath(
                                      '//div[@class="detail__content"]/p')] if
                                  paragraph.strip() != '' and paragraph.strip() != '\xa0' and paragraph.strip() is not None])
        item['abstract'] = item['body'].split('\n')[0]
        soup = BeautifulSoup(response.text, 'lxml')
        item['images'] = [img.get('src') for img in soup.select('.pages-pic img')]
        return item