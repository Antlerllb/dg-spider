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


# author : 梁智霖
class Id360wywSpider(BaseSpider):
    name = 'id_360wyw'
    website_id = 58
    language_id = 1809
    # allowed_domains = ['id.360wyw.com']
    start_urls = ['http://id.360wyw.com/news']
    is_http = 1 #若网站使用的是http协议，需要加上这个类成员(类变量)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('div.guide_mid>ul>li>a')
        for category1 in categories:
            category_url = category1.get('href')
            yield Request(url=category_url, callback=self.parse_page,
                          meta={'category1': category1.get('title')})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        #此网站新闻的年代十分久远
        if OldDateUtil.time is not None:
            last_time = soup.select('div.list_bot > dl > dt > span')[-1].text + " 00:00:00"
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            articles = soup.select(' div.list_bot > dl > dt > a:nth-child(3)')
            for article in articles:
                article_url = article.get('href')
                title = article.text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': response.meta['category1'],'title': title})
        else:
            self.logger.info("时间截止")
        if flag:
            if soup.select('#dataForm > div > a')[-2].text == "下一页":
                next_page = response.url.replace('/news/p1','') + soup.select('#dataForm > div > a')[-2].get('href')
                yield Request(url=next_page, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = response.meta['title']
        pub_time = soup.select_one('#container > div.content > div.listp_left > div.wenz > h4 > span.time').text
        item['pub_time'] = pub_time
        try:
            item['images'] = [img.get('src') for img in soup.select('tr > td > div.img-container > img')]
        except:
            item['images'] = ''
        try:
            item['body'] = ''.join(
                paragraph.text.replace('\n','\r').lstrip().replace('\r\r',"\n") for paragraph in soup.select('div p') if
                 paragraph.text != '' and paragraph.text != ' ')
        except:
            item['body'] = ''
        try:
        #     abstract = soup.select_one('div p').replace('\n','\r').lstrip().replace('\r\r',"\n").text
            abstract = item['body'].split('\n')[0]
            item['abstract'] = abstract
        except:
            item['abstract'] = ''
        yield item