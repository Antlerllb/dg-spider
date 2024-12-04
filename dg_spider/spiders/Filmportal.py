# encoding: utf-8




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

# author: 王晋麟
# check: pys
# pass
class FilmportalSpider(BaseSpider):
    name = 'Filmportal'
    website_id = 1749
    language_id = 1901
    start_urls = ['https://www.filmportal.de/']
    custom_settings = {'RETRY_TIMES': 10,'DOWNLOAD_DELAY': 0.1, 'RANDOMIZE_DOWNLOAD_DELAY': True}

    def parse(self, response):
        category1 = response.xpath('//*[@id="block-mainnavigation"]/ul/li[7]/a/text()').extract()[0]
        sub_url = self.start_urls[0] + response.xpath('//*[@id="block-mainnavigation"]/ul/li[7]/a/@href').extract()[0].replace('/', '')
        yield Request(url=sub_url, callback=self.parse_page, meta={'category1': category1, 'sub_url': sub_url})

    def parse_page(self, response):
        category2 = response.xpath('//*[@id="block-mainpagecontent"]/div/div[1]/div[2]/div/div/div/div/div[2]/a/text()').extract()[0]
        page_url = response.meta['sub_url'] + '/' + response.xpath('//*[@id="block-mainpagecontent"]/div/div[1]/div[2]/div/div/div/div/div[2]/a/@href').extract()[0].split('/')[1]
        yield Request(url=page_url, callback=self.parse_news, meta={'category1':response.meta['category1'], 'category2':category2})

    def parse_news(self, response):
        flag = True
        soup = BeautifulSoup(response.text, "html.parser")
        for news in soup.select("div.site-main--content > div#block-mainpagecontent .views-row"):
            pub_time = news.select(".field")[0].string.split('|')[0].replace(' ', '').split('.')[2] + '-' + news.select(".field")[0].string.split('|')[0].replace(' ', '').split('.')[1] + '-' + news.select(".field")[0].string.split('|')[0].replace(' ', '').split('.')[0] + ' ' + news.select(".field")[0].string.split('|')[1].split(' ')[1] + ':00'  # pub_time
            if OldDateUtil.time is None or int(OldDateUtil.time) <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                try:   # 有p分情况讨论：为图则空，无图则有字
                    abstract = news.select(".clearfix p")[0].text
                except:   # 无p置空,解决赋值前引用
                    abstract = ''
                yield Request(url="https://www.filmportal.de" + news.select(".field > div > a")[0].attrs["href"], callback=self.parse_item, meta={'category1': response.meta['category1'], 'category2': response.meta['category2'],'pub_time': pub_time, 'abstract': abstract})
            else:
                self.logger.info("时间截止")
                flag = False
                break
        if flag:
            try:
                yield Request(url='https://www.filmportal.de/news/news' + soup.select("div#block-mainpagecontent .pager__item--next a")[0].attrs["href"], callback=self.parse_news, meta={'category1': response.meta['category1'], 'category2': response.meta['category2']})
            except:
                pass

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.xpath('//*[@id="block-mainpagecontent"]/div/div[1]/div[1]/div[3]/h1/text()').extract()[0].replace('\n', '').strip()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = '\n'.join([content.text for content in soup.select('.clearfix p')]).strip()
        # 若因外部首个p为图拿不到字，则直接从body里拿第一段. 若全文无内容，则body和abstract都为空
        item['abstract'] = item['body'].split('\n')[0] if response.meta['abstract'] == '' else response.meta['abstract']
        item['pub_time'] = response.meta['pub_time']
        try:   # 新闻页内爬取图片
            item['images'] = ['https://www.filmportal.de' + p.attrs['src'] for p in soup.select(".panel-2col-stacked div:nth-child(1) img")]
        except:
            item['images'] = []
        yield item