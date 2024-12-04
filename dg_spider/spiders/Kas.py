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
from copy import deepcopy

# author: 王晋麟
# check: pys
# pass
class KasSpider(BaseSpider):
    name = 'Kas'
    website_id = 789
    language_id = 1901
    start_urls = ['https://www.kas.de/en/home']
    custom_settings = {'RETRY_TIMES': 10,'DOWNLOAD_DELAY': 0.1, 'RANDOMIZE_DOWNLOAD_DELAY': True}  # 你根据前一个页面才能获取到后一个页面，如果前一个页面获取不到后一个页面也获取不到，所以还是加上这句，如果一次获取不到就重试10次
    year = {
        'January': '1',
        'February': '2',
        'March': '3',
        'April': '4',
        'May': '5',
        'June': '6',
        'July': '7',
        'August': '8',
        'September': '9',
        'October': '10',
        'November': '11',
        'December': '12'
    }

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        category1 = soup.select('.c-main-navigation__list-wrapper li[data-id="subnav-3"] a')[0].text.strip()  # category1
        page_url = soup.select('.c-main-navigation__list-wrapper li[data-id="subnav-3"] a')[0].attrs["href"]
        yield Request(url=page_url, callback=self.parse_news, meta={'category1': category1})

    def parse_news(self, response):
        flag = True
        soup = BeautifulSoup(response.text, "html.parser")
        for news in soup.select(".kas-shuffle > a"):
            time = news.select(".o-metadata--date")[0].string.strip()
            times = time.split(' ')
            response.meta['pub_time'] = times[2] + '-' + self.year[times[0]] + '-' + times[1].replace(',', '') + ' ' + '00:00:00'  # pub_time
            if OldDateUtil.time is None or int(OldDateUtil.time) <= OldDateUtil.str_datetime_to_timestamp(response.meta['pub_time']):
                response.meta['category2'] = news.select(".o-metadata--category")[0].string.strip()  # category2
                try:
                    response.meta['images'] = ['https://www.kas.de' + news.select(".o-tile__image")[0].attrs["src"]]  # picture
                except:
                    response.meta['images'] = []
                news_url = 'https://www.kas.de' + news.attrs["href"]
                yield Request(url=news_url, callback=self.parse_item, meta=deepcopy(response.meta))
            else:
                self.logger.info("时间截止")
                flag = False
                break
        if flag:
            next_page = soup.select("#_com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_PUBLIKATIONEN_ocerSearchContainerPageIterator > div > ul > li")[2]
            next_page_url = next_page.select("a")[0].attrs["href"]  # 翻页
            if next_page_url != 'javascript:;':
                yield Request(url=next_page_url, callback=self.parse_news,meta=deepcopy(response.meta))

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, "html.parser")
        item['pub_time'] = response.meta['pub_time']
        item['title'] = soup.select(".o-page-module--bare-bottom h1, #main-content h2.o-page-headline")[0].text.strip()
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = '\n'.join([content.text.strip() for content in soup.select('.c-page-main__text, .content-text-margin p')])
        try:
            item['abstract'] = soup.select(".c-page-intro__copy")[0].text.strip() if soup.select(".c-page-intro__copy")[0].text.strip() else item['body'].split('\n')[0]
        except:
            item['abstract'] = ''
        item['images'] = response.meta['images'] if response.meta['images'] else []
        yield item