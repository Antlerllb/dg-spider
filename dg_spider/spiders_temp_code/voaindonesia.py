# encoding: utf-8




from scrapy.http.request import Request
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
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

#author: 吴元栩
class VoaindonesiaSpider(BaseSpider):
    name = 'voaindonesia'
    website_id = 386
    language_id = 1952
    type_list = ['299','7014']
    start_urls = [f'https://www.voaindonesia.com/z/{type}?p={i}'for type in type_list for i in range(0,101)]#这两个是新闻集合，其他栏目的新闻在这两个都能找到,新闻量不多
    proxy = '02' # 如果爬虫需要代理，加上这一行成员变量，否则别加。

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        url_list = []
        try:
            url_list.append(soup.find(class_="col-xs-12 col-sm-12 col-md-12 col-lg-12 col-xs-vertical").find("a").get("href"))
            url_list_row = soup.find_all(class_="col-xs-12 col-sm-12 col-md-12 col-lg-12 fui-grid__inner")
            for i in url_list_row:
                url = i.find("a").get("href")
                url_list.append(url)
            for i in url_list:
                url = "https://www.voaindonesia.com" + i
                yield Request(url=url, callback=self.parse_page_content)
        except:
            return

    def parse_page_content(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')

        #文章时间
        pub_time_list = soup.find(class_="date").find("time").get("datetime").split("T")
        pub_time_hour = pub_time_list[1].split("+")[0]
        pub_time = pub_time_list[0]+" "+pub_time_hour

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= OldDateUtil.time:

            #文章标题
            try:
                title = soup.find(class_="title pg-title").text.strip()
            except:
                return

            #文章类型,有一些文章原本就是无标签，所以置为None
            try:
                tag = soup.find(class_="links__item").text.strip()
            except:
                tag = None

            #文章内容
            try:
                body = soup.find(class_="wsw").text.strip()
            except:
                body = soup.find(class_="intro m-t-md").text.strip()
            body = body.replace('\n','')

            #文章图片
            img = []
            artical = soup.find(class_="wsw")
            pic_list = artical.find_all(class_="thumb")
            for i in pic_list:
                pic = i.find("img").get("src")
                img.append(pic)

            #文章简介
            try:
                abstract = soup.find(class_="cover-media").find(class_="caption").text.strip()
            except:
                abstract = soup.find(class_="intro m-t-md").text.strip()

            item = NewsItem(language_id=self.language_id)
            item['title'] = title
            item['category1'] = tag
            item['body'] = body
            item['abstract'] = abstract
            item['pub_time'] = pub_time
            item['images'] = img
            yield item

        else:
            self.logger.info("时间截止")