# encoding: utf-8




from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
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
from scrapy import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author : 吴元栩


class JugantorSpider(BaseSpider):
    name = 'jugantor'
    allowed_domains = ['jugantor.com']
    start_urls = [f"https://www.jugantor.com/all-news?page={i}" for i in range(1,51)]
    website_id = 1922
    language_id = 1799

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        i = soup.select('a')
        news_list_old = []
        for news_url in i:
            news_list_old.append(news_url.get('href'))
        news_list_old = news_list_old[124:164]
        news_list = sorted(set(news_list_old), key=news_list_old.index)
        for i in news_list:
            yield Request(url=i, callback=self.parse_page_content)

    def parse_page_content(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')

        #文章标题
        page_title = soup.select_one('#news-title > h3').text
        print(page_title)

        #文章时间,按年月日
        page_time_raw = soup.select_one("#rpt-date > div.row.row-cols-2.pb-2 > div:nth-child(1) > div:nth-child(2) ").text
        page_time_deal = page_time_raw.split(',', 1)
        date = page_time_deal[0]
        datel = date.split(" ")
        day = datel[1]
        dayf = str(OldDateUtil.BN_1779_DATE[list(day)[0]])
        days = str(OldDateUtil.BN_1779_DATE[list(day)[1]])
        month = str(OldDateUtil.BN_1779_DATE[datel[2]]).zfill(2)
        year = datel[3]
        year1 = str(OldDateUtil.BN_1779_DATE[list(year)[0]])
        year2 = str(OldDateUtil.BN_1779_DATE[list(year)[1]])
        year3 = str(OldDateUtil.BN_1779_DATE[list(year)[2]])
        year4 = str(OldDateUtil.BN_1779_DATE[list(year)[3]])
        pub_time = "{}{}{}{}-{}-{}{}".format(year1,year2,year3,year4,month,dayf,days)

        #文章内容
        page_paragraph_above = soup.select('#myText >p')#//*[@id="myText"]/p[1]/text()
        page_paragraph = ""
        for i in page_paragraph_above :
            page_paragraph+=i.text+'\n'

        #图片网址
        page_picture_above = soup.find_all(class_="dtl-news-img")
        img_href = re.findall(r'href="(.*?)"',str(page_picture_above))

        item = NewsItem(language_id=self.language_id)
        item['category1'] = 'news'
        item['title'] = page_title
        item['pub_time'] = pub_time
        item['body'] = page_paragraph
        item['abstract'] = item['body'].split('\n')[0]
        item['images'] = img_href
        # time.sleep(5)
        return item
