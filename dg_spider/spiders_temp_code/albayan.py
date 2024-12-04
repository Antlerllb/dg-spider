import re
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from scrapy import Selector
from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil





class AlbayanSpider(BaseSpider):
    name = "albayan"
    website_id = 2642  # id一定要填对！
    language_id = 1748
    author = "张博为"
    start_urls = ["https://www.albayan.ae/"]
    sum = 0

    @staticmethod
    def extract_date(url):
        pattern = r'/(\d{4}-\d{2}-\d{2})-'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        menu_items = soup.select('#navigation > section.container-fluid > section.row > ul.menu > li')

        for cnt, item in enumerate(menu_items):
            if cnt in [0, 3, 11]:
                continue

                # Gather URLs from each section
            if cnt in [6, 8, 10]:
                first_url = item.select_one('a')['href']
                yield Request(url=first_url, callback=self.parse_news, meta={'dont_redirect': True}, dont_filter=True)
            else:
                sub_items = item.select('ul.sub-menu > li')
                for sub_item in sub_items:
                    sec_url = sub_item.select_one('a')['href']
                    yield Request(url=sec_url, callback=self.parse_news, meta={'dont_redirect': True}, dont_filter=True)

            if self.sum >= 2000:
                break

    def parse_news(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.select(
            'body.section-page.albayan > section.container-fluid > section.row > section.twocolumnsctky > #mainarea > div.section > ul > li')

        for news in news_items:
            if self.sum >= 2000:
                return
            href_tag = news.select_one('figure.media > a')
            if not href_tag:
                continue

            href = href_tag['href']
            date = self.extract_date(href)
            if date:
                date += " 00:00:00"

            if OldDateUtil.time and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(date):
                return

            sec_title = news.select_one('div.category > a').text.strip()
            title = news.select_one('h3').text.strip()

            yield Request(url=href, callback=self.parse_item,
                          meta={'title': title, 'category1': sec_title, 'pub_time': date})

    def parse_item(self, response):
        sel = Selector(response)
        soup = BeautifulSoup(response.text, 'html.parser')

        img = soup.select_one('figure > img, div.media.author > a > img, div.media > img')
        img_src = img['src'] if img else ''
        img_url = response.urljoin(img_src)

        texts = soup.select('div.articlecontent > p')
        if texts is None:
            texts = soup.select('div.articlecontent > div')
        if len(texts) is not 1:
            body = '\n'.join(p.text.strip() for p in texts)
        else:
            body = texts[0].text.strip() if texts else ''
        abstract = ''
        for i in texts:
            if i is not None:
                abstract = i.text.strip() if texts else ''
                break
        if abstract == '':

            abstract = 'no'
            body = 'no'

        item = NewsItem(
            title=response.meta['title'],
            category1=response.meta['category1'],
            pub_time=response.meta['pub_time'],
            images=[img_url],
            abstract=abstract,
            body=body
        )

        self.sum += 1
        if self.sum>2050:
            return
        yield item