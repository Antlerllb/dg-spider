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

Urdu_Month = {
    'جنوری': '01',
    'فروری': '02',
    'مارچ': '03',
    'اپریل': '04',
    'مئی': '05',
    'جون': '06',
    'جولائی': '07',
    'اگست': '08',
    'ستمبر': '09',
    'اکتوبر': '10',
    'نومبر': '11',
    'دسمبر': '12'
}
# check:wpf pass
# author : 梁智霖
class Dailykhabrain_deSpider(BaseSpider):
    name = 'dailykhabrain'
    website_id = 2097  #id未填
    language_id = 2238 #乌尔都语
    #allowed_domains = ['dailykhabrain.com.pk']
    start_urls = ['https://dailykhabrain.com.pk/']
    # is_http = 1 #若网站使用的是http协议，需要加上这个类成员(类变量)
    # 有时候会报403...文章没有问题

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('div.menu-container > div > ul > li > a')[2:12] #视频不爬
        for category1 in categories:
            category_url = category1.get('href')
            yield Request(url=category_url, callback=self.parse_page,
                          meta={'category1': category1.text})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        try:
            if OldDateUtil.time is not None:
                tn = soup.select('div.col-xs-12.col-sm-7.col-md-6 > div > div > span:nth-child(2)')[-1].text.split(' ')
                ty = soup.select('div.col-xs-12.col-sm-7.col-md-6 > div > div')[-1].text.split('\n\xa0')[1].split('\xa0')
                tr = soup.select('div.col-xs-12.col-sm-7.col-md-6 > div > div > span:nth-child(1)')[-1].text
                if int(tr) < 10:
                    tr = "0" + tr
                last_time = tn[1] + "-" + Urdu_Month[ty[0]] + "-" + str(tr) + "00:00:00"

            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                articles = soup.select('div.col-xs-12.col-sm-7.col-md-6 > div')
                for article in articles:
                    article_url = article.select_one('h3 > a').get('href')
                    title = article.select_one('h3 > a').text.lstrip()
                    tn = soup.select('div.col-xs-12.col-sm-7.col-md-6 > div > div > span:nth-child(2)')[-1].text.split(' ')
                    ty = soup.select('div.col-xs-12.col-sm-7.col-md-6 > div > div')[-1].text.split('\n\xa0')[1].split('\xa0')
                    tr = soup.select('div.col-xs-12.col-sm-7.col-md-6 > div > div > span:nth-child(1)')[-1].text
                    if int(tr) < 10:
                        tr = "0" + tr
                    pub_time = tn[1] + "-" + Urdu_Month[ty[0]] + "-" + str(tr) + "00:00:00"
                    yield Request(url=article_url , callback=self.parse_item, meta={'category1': response.meta['category1'],
                    'title': title,'pub_time': pub_time})
            else:
                self.logger.info("时间截止")
            if flag:
                next_page = soup.select_one('div.col-xs-12.col-sm-12.col-md-8 > nav > div > a.next.page-numbers').get('href')
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
        try:
            item['images'] = [img.get('src') for img in soup.select('article > img')]
        except:
            item['images'] = None
        try:
            item['body'] = ''.join(
                paragraph.text.lstrip() for paragraph in soup.select('div.entry-content > p')  if
                 paragraph.text != '' and paragraph.text != ' ')
        except:
            item['body'] = ''
        item['abstract'] = item['body'].split('\n')[0]
        yield item