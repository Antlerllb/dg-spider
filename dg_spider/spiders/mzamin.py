import time

from scrapy import Selector
from scrapy.exceptions import CloseSpider
from scrapy.http.request import Request
from bs4 import BeautifulSoup

from dg_spider.items import NewsItem
from dg_spider.libs.base_spider import BaseSpider

class MzaminaSpider(BaseSpider):
    name = 'mzamin'
    website_id = 2268
    language_id = 1779
    author = '王晋麟'

    base_url = 'https://mzamin.com/archivedNews.php?data={}&date={}'
    day = 0

    @staticmethod
    def make_args(day):
        stamp = int(time.time()) - day * 86400
        format_time = time.strftime("%Y-%m-%d", time.localtime(int(stamp)))
        time_stamp = int(time.mktime(time.strptime(format_time, "%Y-%m-%d")))
        return format_time, time_stamp

    def start_requests(self):
        format_time, time_stamp = self.make_args(self.day)
        self.day += 1
        yield Request(url=self.base_url.format(time_stamp, format_time),
                      callback=self.parse, meta={'format_time': format_time + ' 00:00:00'})

    def parse(self, response, **kwargs):
        sel = Selector(response)
        news_lis = sel.css('.my-3')
        for news in news_lis:
            news_url = news.css('h1 a::attr(href)').get()
            news_title = news.css('h1 a::text').get().strip()
            yield Request(url=response.urljoin(news_url), callback=self.parse_item,
                          meta={'title': news_title,
                                'format_time': response.meta['format_time']})
        format_time, time_stamp = self.make_args(self.day)
        self.day += 1
        yield Request(url=self.base_url.format(time_stamp, format_time),
                      callback=self.parse, meta={'format_time': format_time + ' 00:00:00'})

    def parse_item(self, response):
        sel = Selector(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem()
        item['category1'] = 'সংবাদ'
        item['title'] = response.meta['title'] if response.meta['title'] != '' else sel.css('.col-sm-8 h1.fs-1::text').get().strip()
        item['pub_time'] = response.meta['format_time']
        item['images'] = [response.urljoin(img.css('img::attr(data-src)').get()).replace(' ', '') for img in sel.css('.col-sm-8 .img-fluid')]
        item['body'] = '\n'.join([' '.join(content.text.replace('\xa0', '').replace('\n', '').strip().split()) for content in soup.select('.col-sm-8 .fs-5 p') if content.text.strip() != ''])
        item['abstract'] = item['body'].split('\n')[0].strip() if item['body'].split('\n')[0] != '' and len(item['body'].split('\n')[0]) < 100 else item['body'].split('।')[0].strip()
        if len(item['body'].split('\n')) == 1:
            item['body'] = item['abstract'].strip() + '\n' + item['body'].strip()
        item['language_id'] = self.language_id
        yield item


if __name__ == '__main__':
    from scrapy import cmdline
    command = "scrapy crawl mzamin -a json_path=json/spider.json"
    cmdline.execute(command.split())
