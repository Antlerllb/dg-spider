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


class germancriSpider(BaseSpider): # author：田宇甲
    name = 'germancri'  # 无需翻页,全在一页
    website_id = 1794
    language_id = 1898
    start_urls = [f'https://german.cri.cn/{i}/index.shtml' for i in ['umwelt']]
    # proxy = '02'

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' .column_wrapper .german_list ul li'):
            ssd = i.select_one(' .subtime').text.split(' ')[0].split('.')
            time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' ' + i.select_one(' .subtime').text.split(' ')[1]
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                meta = {'pub_time_': time_, 'title_': i.select_one(' .tit').text, 'abstract_': i.select_one(' .brief').text,  'category1_': response.url.split('cri.cn/')[1].split('/index')[0], 'images_': [i.select_one(' .img_box a img')['src']]}
                yield Request(i.select_one(' .tit h3 a')['href'], callback=self.parse_item, meta=meta)


    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .content_area').text.strip().strip('\n') if soup.select_one(' .content_area') is not None else soup.select_one(' .detailMod-body.noVideoJs').text.strip().strip('\n')
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
