


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
#author: 蔡卓妍
class BpkSpider(BaseSpider):
    name = 'bpk'
    website_id = 121
    language_id = 1952
    start_urls = ['https://www.bpk.go.id/archive/news/berita-utama',
                  'https://www.bpk.go.id/archive/news/siaran-pers-63'] #新闻+新闻稿

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        flag = True
        last_time = datetime.datetime.strptime(soup.select(".entry")[-1].select_one(".entry-meta").text.strip(),'%d %b %Y')
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
            category1 = soup.select_one("#page-title h1").text
            lists = soup.select(".entry")
            for i in lists:
                title = i.select_one(".entry-title h2").text
                pub_time = datetime.datetime.strptime(i.select_one(".entry-meta").text.strip(),'%d %b %Y')
                img = i.select_one(".entry-image >a").get("href")
                article = i.select_one(".entry-title a").get("href")
                meta = {'pub_time': pub_time,'title':title,'img':img,'category1':category1}
                yield Request(url=article, callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            next_page = soup.select_one(".index_paging_next >a").get("href")
            yield Request(url=next_page, callback=self.parse)

    def parse_item(self,response):
        soup = BeautifulSoup(response.text,"html.parser")
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta["title"]
        item['category1'] = response.meta['category1']
        try:
            item['body'] = "\n".join(i.text.strip() for i in (soup.find_all(style="text-align: justify;")))
            item['abstract'] = soup.find(style="text-align: justify;").text
        except:
            try:
                item['body'] = "\n".join(i.text.strip() for i in (soup.select(".newsli")))
                item['abstract'] = soup.select_one("newsli").text
            except:
                item['body'] = "".join(i.text.strip() for i in (soup.select('div.entry-content.notopmargin p')))
                item['abstract'] = soup.select_one('div.entry-content.notopmargin p').text
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [response.meta['img']] + [i.select_one('img').get('src') for i in (soup.find_all(style="text-align: center;"))]
        yield item