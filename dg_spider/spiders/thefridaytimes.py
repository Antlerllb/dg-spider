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

# author : 梁智霖
class Thefridaytimes_deSpider(BaseSpider):
    name = 'thefridaytimes'
    website_id = 2099 #id未填
    language_id = 1866 #英语
    #allowed_domains = ['thefridaytimes']
    start_urls = ['https://www.thefridaytimes.com/']
    # is_http = 1 #若网站使用的是http协议，需要加上这个类成员(类变量)
    # 大部分是英语，少部分是乌尔都语

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        categories = soup.select('div.jeg_mainmenu_wrap > ul > li > a')[1:10]
        del categories[5]  # video不爬
        for category1 in categories:
            category_url = category1.get('href')
            yield Request(url=category_url, callback=self.parse_page,
                          meta={'category1': category1.text})

    def parse_page(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        flag = True
        try:
            if OldDateUtil.time is not None:
                tnyr = soup.select(
                    "div.jeg_posts_wrap > div > article > div.jeg_postblock_content > div.jeg_post_meta > div.jeg_meta_date > a")[-1].text.split(' ')
                if int(tnyr[2].split(',')[0]) < 10:
                    tnyr = "0" + tnyr
                last_time = tnyr[3] + "-" + month[tnyr[1]] + "-" + str(tnyr[2].split(',')[0]) + " 00:00:00"
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                articles = soup.select('div.jeg_block_container > div.jeg_posts_wrap > div > article')
                for article in articles:
                    article_url = article.select_one('div.jeg_postblock_content > h3 > a').get('href')
                    title = article.select_one('div.jeg_postblock_content > h3 > a').text.lstrip()
                    tnyr = soup.select_one(
                        "div.jeg_posts_wrap > div > article > div.jeg_postblock_content > div.jeg_post_meta > div.jeg_meta_date > a").text.split(' ')
                    if int(tnyr[2].split(',')[0]) < 10:
                        tnyr = "0" + tnyr
                    pub_time = tnyr[3] + "-" + month[tnyr[1]] + "-" + str(tnyr[2].split(',')[0]) + " 00:00:00"
                    images = [article.select_one('div.jeg_thumb > a > div > img').get('src')]
                    yield Request(url=article_url , callback=self.parse_item, meta={'category1': response.meta['category1'],
                    'title': title,'pub_time': pub_time,'images':images})
            else:
                self.logger.info("时间截止")
            if flag:
                if soup.select_one('a.page_nav.next').text:
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
            # 有两种文章格式
            if soup.select('div.entry-content.no-share > div.content-inner.jeg_link_underline > p'):
                item['body'] = ''.join(
                    paragraph.text.lstrip() for paragraph in soup.select('div.entry-content.no-share > div.content-inner.jeg_link_underline > p')
                   if paragraph.text != '' and paragraph.text != ' ')
            else:
                item['body'] = ''.join(
                    paragraph.text.lstrip() for paragraph in
                    soup.select('div.entry-content.no-share > div.content-inner.jeg_link_underline > h4')
                    if paragraph.text != '' and paragraph.text != ' ')
        except:
            item['body'] = ''
        item['abstract'] = item['body'].split('\n')[0]
        yield item