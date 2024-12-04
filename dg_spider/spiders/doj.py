import bs4, requests



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

ENGLISH_MONTH = {
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
    'December': '12'}


class dojSpider(BaseSpider):  # author：田宇甲 我喂自己袋盐
    name = 'doj'  # 所有新闻都在一页，有些文章有链接但是文章本身已经被删除了
    website_id = 1264  # 本地测试403较少
    language_id = 1866
    start_urls = ['https://doj.gov.ph/news.html']
    proxy = '02'
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac O\S X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'}

    def parse(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        now = soup.select_one(' .col-md-12 article a')['href'].split('newsid=')[1]
        for i in range(8, int(now)):
            url = 'https://doj.gov.ph/news_article.html?newsid=' + str(int(now) - i + 8)
            try:  # 有些链接里面的新闻被删除了
                time_in = bs4.BeautifulSoup(requests.get(url, headers=dojSpider.header).text, 'html.parser').select_one(' .portfolio-meta').text.split()
                time_ = time_in[-1] + '-' + OldDateUtil.EN_1866_DATE[time_in[1]] + '-' + time_in[0] + ' 00:00:00'
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    meta = {'time_': time_in[-1] + '-' + OldDateUtil.EN_1866_DATE[time_in[1]] + '-' + time_in[0] + ' 00:00:00'}
                    yield Request(url, callback=self.parse_item, meta=meta)
            except Exception as e:
                continue


    def parse_item(self, response):
        try: # 有的只是公告，没有文字
            item = NewsItem(language_id=self.language_id)
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            item['title'] = soup.select_one(' .block h2').text
            item['category1'] = 'News-Release'
            item['category2'] = None
            item['body'] = soup.select_one(' .post-content').text
            item['abstract'] = soup.select_one(' .post-content p').text
            item['pub_time'] = response.meta['time_']
            item['images'] = 'https://doj.gov.ph/'+soup.select_one(' .post-img img')['src']
            yield item
        except:
            pass
