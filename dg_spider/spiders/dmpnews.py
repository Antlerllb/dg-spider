import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
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


class DmpnewsSpider(BaseSpider):
    name = 'dmpnews'
    website_id = 2270
    author = '刘雨鑫'
    language_id = 1779
    start_urls = ['https://dmpnews.org']
    lan_num = 1

    @staticmethod
    def translate_time(time_list):
        lst1 = time_list.split('T')[0]
        lst2 = time_list.split('T')[1].split('+')[0]
        rough_time = ''
        detail_time = ''
        for i in lst1.split('-'):
            a = ''
            for j in i:
                a += str(OldDateUtil.BN_1779_DATE[j])
            rough_time += a + '-'
        for i in lst2.split(':'):
            b = ''
            for j in i:
                b += str(OldDateUtil.BN_1779_DATE[j])
            detail_time += b + ':'
        pub_time = rough_time.strip('-') + ' ' + detail_time.strip(':')
        return pub_time

    @staticmethod
    def clear(ss):
        f_list = []
        for i in ss.split('\n'):
            if i != '':
                f_list.append(i)
        result = ''
        for i in f_list:
            result += i
            if i != f_list[-1]:
                result += '\n'
        return result

    @staticmethod
    def clear_none(ss):
        ss_list = [i for i in ss.split(' ') if i != '']
        result = ''
        for i in ss_list:
            result += i.replace('\t', '').replace('\r', '').replace('\xa0', '')
            if i != ss_list[-1]:
                result += ' '
        return result

    @staticmethod
    def correct_news(title, abstract, body):
        body = DmpnewsSpider.clear_none(DmpnewsSpider.clear(body))
        body = DmpnewsSpider.clear(body)
        title = DmpnewsSpider.clear_none(DmpnewsSpider.clear(title))
        if abstract != '':
            abstract = DmpnewsSpider.clear_none(DmpnewsSpider.clear(abstract))
        if abstract == '':
            abstract = body.split('\n')[0]
        if len(body.split('\n')) == 1 and abstract != '':
            body = abstract + '\n' + body
        return title, abstract, body

    def parse(self, response):
        class_url_list = response.xpath('//ul[@id="menu-td-demo-header-menu-1"]//li')
        class_url_list.pop(0)
        class_url_list.pop(0)
        for li in class_url_list:
            class_url = li.xpath('./a/@href').extract_first()
            if class_url.startswith('https://dmpnews.org'):
                response.meta['category1'] = li.xpath('./a/text()').extract_first()
                yield scrapy.Request(class_url, callback=self.parse_page, meta=response.meta)

    def parse_page(self, response):
        block = response.xpath('//div[@class="main-col"]//div[@itemtype="http://schema.org/Article"]')
        # print(block)
        for i in block:
            time_list = i.xpath('.//time/@datetime').extract_first()
            pub_time = self.translate_time(time_list)
            # print(pub_time)
            if OldDateUtil.time is not None and OldDateUtil.time > OldDateUtil.str_datetime_to_timestamp(pub_time):
                return
            detail_url = i.xpath('.//h2/a/@href').extract_first()
            # print(detail_url)
            response.meta['pub_time'] = pub_time
            yield scrapy.Request(detail_url, callback=self.parse_item, meta=response.meta)
        next_url = response.xpath('//div[@class="pagination"]//a[text()="›"]/@href').extract_first()
        if next_url is None:
            return
        yield scrapy.Request(next_url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        pub_time = response.meta['pub_time']
        category1 = response.meta['category1']
        title = response.xpath('//h1[@class="post-tile entry-title"]/text()').extract_first()
        images = []
        out_image = response.xpath('//div[@class="feature-img"]/img/@src').extract_first()
        if out_image is not None:
            images.append(out_image)
        in_images = response.xpath('//div[@class="entry-content"]//p/img')
        for i in in_images:
            image = i.xpath('./@src').extract_first()
            if image is not None:
                images.append(image)
        abstract = ''
        body = ''
        p_list = response.xpath('//div[@class="entry-content"]//p | //div[@class="entry-content"]//div[@style="text-align: justify"] | //div[@class="news_details inner_news_details"]')
        for i in p_list:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace('\n', '')
            body += p + '\n'
        title, abstract, body = self.correct_news(title, abstract, body)
        item['title'] = title
        item['abstract'] = abstract
        item['body'] = body
        item['category1'] = category1
        item['images'] = images
        item['pub_time'] = pub_time
        if body != '':
            yield item



