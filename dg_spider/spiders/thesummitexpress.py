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


# author:武洪艳
class ThesummitexpressSpider(BaseSpider):
    name = 'thesummitexpress'
    website_id = 1171
    language_id = 1866
    start_urls = ['https://www.thesummitexpress.com/search/label/News%20and%20Events/']  # https://www.thesummitexpress.com/search/label/News%20and%20Events

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        flag = True
        articles = soup.select('div.blog-posts.hfeed > div')
        if OldDateUtil.time is not None:
            t = articles[-1].select_one('#meta-post a.timestamp-link').text.replace(',', ' ').split(' ')
            last_time = "{}-{}-{}".format(t[5], str(OldDateUtil.EN_1866_DATE[t[2]]).zfill(2), t[3]) + ' 00:00:00'
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
            for article in articles:
                tt = article.select_one('#meta-post a.timestamp-link').text.replace(',', ' ').split(' ')
                pub_time = "{}-{}-{}".format(tt[5], str(OldDateUtil.EN_1866_DATE[tt[2]]).zfill(2), tt[3]) + ' 00:00:00'
                article_url = article.select_one('h2.post-title.entry-title a').get('href')
                title = article.select_one('h2.post-title.entry-title a').text
                yield Request(url=article_url, callback=self.parse_item, meta={'category1': 'news', 'title': title, 'pub_time': pub_time})
        else:
            flag = False
            self.logger.info("时间截止")
        if flag:
            if soup.select_one('#Blog1_blog-pager-older-link') == None:
                self.logger.info("no more pages")
            else:
                next_page = soup.select_one('#Blog1_blog-pager-older-link').get('href')
                yield Request(url=next_page, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        item['category1'] = response.meta['category1']
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['images'] = [img.get('src') for img in soup.select('article.post-article img')]
        item['body'] = '\n'.join(
            [paragraph.text.strip() for paragraph in soup.select('.post-body.entry-content') if
             paragraph.text != '' and paragraph.text != ' '])
        item['abstract'] = item['body'].split('\n')[0]
        yield item
