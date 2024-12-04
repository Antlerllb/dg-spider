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



# author:吴元栩
class CeiSpider(BaseSpider):
    name = 'cei'
    website_id = 2930
    language_id = 1866
    types = ["legal_brief","congressional_testim","regulatory_comments","coalition_letters","cei_planet","blog","news_releases","opeds_articles","studies"]
    start_urls = [f'https://cei.org/{type}/page/{i}/' for type in types for i in range(1,2)]#),(f"https://cei.org/event/page/{i}/?event-status=past" for i in range(1,810))]

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            url_list = soup.find_all(class_="card-link")
            for i in url_list:
                url = i.get("href")
                yield Request(url=url, callback=self.parse_page_content)
        except:
            return

    def parse_page_content(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')

        # 文章时间
        pub_time = soup.find(class_="posted-on").find("time").get("datetime")

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= OldDateUtil.time:

            # 文章标题
            title = soup.find(class_="entry-title").text.strip()

            # 文章类型
            category1 = soup.find(class_="status").text.strip()
            try:
                category2 = soup.find(class_="meta-wrapper").text.strip()
            except:
                category2 = None

            # 文章内容
            try:
                body = soup.find(class_="entry-content").text.strip()
            except:
                body = None

            # 文章简介
            try:
                abstract = soup.find(class_="entry-subtitle").text.strip()
            except:
                abstract = body.split("\n")[0]

            # 文章图片
            img = []
            try:
                img.append(soup.find(class_="featured-image").get("src"))
            except:
                img.append(None)

            # 文章PDF
            try:
                pdf_link = soup.find(class_="document-link").get("href")
            except:
                pdf_link = None

            item = NewsItem(language_id=self.language_id)
            item['title'] = title.strip()
            item['category1'] = category1
            item['category2'] = category2
            item['body'] = body
            item['abstract'] = abstract
            item['pub_time'] = pub_time
            item['images'] = img
            print(pdf_link)
            print(item['category1'])
            print(item['category2'])


            yield item
        else:
            self.logger.info("时间截止")
