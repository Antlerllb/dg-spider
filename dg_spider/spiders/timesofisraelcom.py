# encoding: utf-8
from copy import deepcopy



import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author：欧炎镁
class TimesofisraelcomSpider(BaseSpider):
    name = 'timesofisraelcom'
    allowed_domains = ['timesofisrael.com']
    start_urls = ['http://timesofisrael.com/']

    website_id = 1935
    language_id = 1866
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'RETRY_TIMES': 20,'DOWNLOAD_DELAY': 0.1, 'RANDOMIZE_DOWNLOAD_DELAY': True}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

    category_api = 'https://www.timesofisrael.com/wp-content/themes/rgb/ajax/topics_for_terms.php?taxonomy=category&term_id={}&post_tag=&before_date={}&numposts=15&is_mobile=false&post_type=&is_load_more=0'
    blog_api = 'https://blogs.timesofisrael.com/wp-content/themes/rgb/ajax/ordering_load_content.php?action=ordering-load-content&object_type=latest&object_id=&paged={}'
    pageit = 1
    # proxy = '02'

    def parse(self, response):
        a_obj_list = response.css('ul.main-menu-footer li a')[1:-1]
        for a_obj in a_obj_list:
            page_link = a_obj.css('::attr(href)').extract_first()
            meta = {'category1': a_obj.css('::text').extract_first().strip()}
            yield scrapy.Request(page_link, callback=self.parse_page,meta=deepcopy(meta),headers=self.headers)

    def parse_page(self, response):
        flag = True
        div_obj_list = response.css('div.item.template1.news div.item-content,div.block.cols5 div.item:not(.load-more)')
        if not div_obj_list:
            div_obj_list = response.css('div.item:not(.load-more)')
        if div_obj_list:
            if OldDateUtil.time is not None:
                try:
                    last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj_list[-1].css('div.date,span.overline.date').xpath('string(.)').extract_first().strip(),'%B %d, %Y, %I:%M %p'))
                except:
                    last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj_list[-1].css('div.date,span.overline.date').xpath('string(.)').extract_first().strip(),'%b %d, %Y, %I:%M %p'))
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(last_time) >= OldDateUtil.time:
                for div_obj in div_obj_list:
                    response.meta['abstract'] = div_obj.css('div.underline a').xpath('string(.)').extract_first().strip()
                    response.meta['title'] = div_obj.css('div.headline a').xpath('string(.)').extract_first().strip()
                    try:
                        response.meta['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj.css('div.date,span.overline.date').xpath('string(.)').extract_first().strip(),'%B %d, %Y, %I:%M %p'))
                    except:
                        response.meta['pub_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(div_obj.css('div.date,span.overline.date').xpath('string(.)').extract_first().strip(),'%b %d, %Y, %I:%M %p'))
                    item_link = div_obj.css('div.headline a::attr(href)').extract_first()
                    yield scrapy.Request(url=item_link, callback=self.parse_item, meta=deepcopy(response.meta),headers=self.headers)
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:
                if response.meta['category1'] != 'The Blogs':
                    detail_link = self.category_api.format(response.css('div.item.load-more a::attr(data-term_id)').extract_first(),response.css('div.item.load-more a::attr(data-before_date)').extract_first())
                else:
                    detail_link = self.blog_api.format(self.pageit)
                    self.pageit += 1
                yield scrapy.Request(detail_link, callback=self.parse_page, meta=deepcopy(response.meta),headers=self.headers)

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title']
        item['pub_time'] = response.meta['pub_time']
        item['category1'] = response.meta['category1']
        item['category2'] = None
        item['abstract'] = response.meta['abstract'] if response.meta['abstract'] != '' else item['title']
        body = response.css('div.the-content >*:not(div):not(script)').xpath('string(.)').extract()
        if not body:
            body = response.css('div.article-content >*:not(div):not(script),div.article-content div:not([class]):not([id])').xpath('string(.)').extract()
        item['body'] = '\n'.join([i.strip() for i in body if i.strip() != ''])
        item['images'] = response.css('div.wp-caption,div.media >a[rel^=lightbox]').css('::attr(src)').extract()
        yield item
