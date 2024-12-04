from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
import re

# check:wpf pass


class BilddeSpider(BaseSpider):  # author：田宇甲
    name = 'bildde'  # 需要代理
    website_id = 1766
    language_id = 1898
    start_urls = [f'https://www.bild.de/news/newsticker/tb-artikel-54190482,contentContextId=54190480,isVideoStartseite=false,page={i},view=ajax,zeigeTSLink=true.bild.html' for i in range(0, 9)]  # 这个网站只有最近24小时的新闻，非常新鲜但是以前的新闻找不到了
    proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.find_all(class_=re.compile('hentry overlay t10ont')):
            try:  # 有的不是新闻
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(i.time).split('datetime="')[1].split('+')[0].replace('T', ' ')) >= int(OldDateUtil.time):
                    meta = {'pub_time_': str(i.time).split('datetime="')[1].split('+')[0].replace('T', ' '), 'title_': i.select_one(' .entry-title').text.strip(), 'category1_': i.select_one(' .channel').text, 'abstract_': i.select_one(' .entry-content').text, 'images_': [i.select_one(' .photo')['src']]}
                    yield Request('https://www.bild.de'+i.a['href'], callback=self.check_check, meta=meta)
            except:
                pass

    def check_check(self, response):
        item, soup = NewsItem(), BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .article-body').text.strip().strip('\n')
        item['abstract'] = response.meta['abstract_'].strip('\n').strip()
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item

#没输出
