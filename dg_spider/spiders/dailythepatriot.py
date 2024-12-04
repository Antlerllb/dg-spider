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

month = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }

# check: wpf pass
# author : 梁智霖
class Dailythepatriot_deSpider(BaseSpider):
    name = 'dailythepatriot'
    website_id = 2096  #id未填
    language_id = 1866 #英语
    #allowed_domains = ['dailythepatriot']
    start_urls = ['https://dailythepatriot.com/']
    # is_http = 1 #若网站使用的是http协议，需要加上这个类成员(类变量)
    # 经常会403...，文章没有问题，建议时间戳传入大一点

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('div.container > div > div > div > div > div > ul > li > a')[1:9] #电子书不爬
        for category1 in categories:
            category_url = category1.get('href')
            yield Request(url=category_url, callback=self.parse_page,
                          meta={'category1': category1.text})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        try:
            if OldDateUtil.time is not None:
                tny = soup.select_one("article:nth-child(11) > div.jeg_postblock_content > div.jeg_post_meta > div.jeg_meta_date > a").text.split(' ')
                tr = tny[2].split(',')[0]
                if int(tr) < 10:
                    tr = "0" + tr
                last_time = tny[3] + "-" + month[tny[1]] + "-" + str(tr) + " 00:00:00"
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                articles = soup.select('div.jeg_posts.jeg_load_more_flag > article')
                for article in articles:
                    article_url = article.select_one('div.jeg_postblock_content > h3 > a').get('href')
                    title = article.select_one('div.jeg_postblock_content > h3 > a').text.lstrip()
                    tny = soup.select_one(
                        "div.jeg_postblock_content > div.jeg_post_meta > div.jeg_meta_date > a").text.split(' ')
                    tr = tny[2].split(',')[0]
                    if int(tr) < 10:
                        tr = "0" + tr
                    pub_time = tny[3] + "-" + month[tny[1]] + "-" + str(tr) + " 00:00:00"
                    images = [article.select_one('div.jeg_thumb > a > div > img').get('src')]
                    yield Request(url=article_url , callback=self.parse_item, meta={'category1': response.meta['category1'],
                    'title': title,'pub_time': pub_time,'images':images})
            else:
                self.logger.info("时间截止")
            if flag:
                if soup.select_one('a.page_nav.next > span').text:
                    next_page = soup.select_one('a.page_nav.next').get('href')
                    yield Request(url=next_page, callback=self.parse_page, meta=response.meta)
        except:
            self.logger.info('no more pages.')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = response.meta['images']
        try:
            #有两种文章格式
            if soup.select('div.entry-content.no-share > div.content-inner > figure > figcaption') and soup.select('div.entry-content.no-share > div.content-inner > p'):
                item['body'] = ''.join(
                    paragraph.text.lstrip() for paragraph in soup.select('div.entry-content.no-share > div.content-inner > p')
                    + soup.select('div.entry-content.no-share > div.content-inner > figure > figcaption') if
                     paragraph.text != '' and paragraph.text != ' ')
            else:
                item['body'] = ''.join(
                    paragraph.text.lstrip() for paragraph in  soup.select('div.entry-content.no-share > div.content-inner > p')
                    if paragraph.text != '' and paragraph.text != ' ')
        except:
            item['body'] = ''
        item['abstract'] = item['body'].split('\n')[0]
        yield item