import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil



from lxml import etree
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





class QdndvnSpider(BaseSpider):  # 类名重命名
    author = "彭海杰"
    name = 'qdndvn'  # name重命名，长度超过5个字符
    language_id = 2242  # 语言id 2242
    website_id = 2055  # 网站id
    start_urls = ['https://www.qdnd.vn/']
    tim = time.time()-24*60*60*3

    def parse(self, response):

        response = etree.HTML(response.text)
        menu = response.xpath('//section[@class="menu-mobile"]/ul/li/a/@href')
        for category_link in menu:
            # print(category_link)
            yield scrapy.Request(url=category_link,callback=self.category_parse)

    def category_parse(self,response):
        response = etree.HTML(response.text)
        news_list = response.xpath('//div[@class="list-news-category"]/article')
        for one in news_list:
            link = one.xpath('a/@href')[0]
            meta = {}
            meta['abstract'] = one.xpath('p[@class="hidden-xs"]/text()')
            meta['pub_time'] = one.xpath('p[@class="hidden-xs pubdate"]/text()')
            if meta['pub_time']:
                s = meta['pub_time'][0]
                s = s.split('/')
                j = s[2].split(' ')
                time = f'{j[0]}-{s[1]}-{s[0]} {j[1]}:00'
            else:
                time = None
            meta['pub_time']  = time
            if OldDateUtil.time == None or OldDateUtil.format_time3(time) >= int(OldDateUtil.time):
                yield scrapy.Request(url=link,callback=self.news_detail,meta=meta)
            else:
                # print('时间截止')
                self.logger.info('时间截止')
                return
        is_next_page = response.xpath('//a/i[@class="fa fa-angle-right"]')
        if len(is_next_page):
            next_page = response.xpath('//div[@class="ex_page"]/a/@href')[-1]
            yield scrapy.Request(url='https://www.qdnd.vn/'+next_page,callback=self.category_parse)

    def news_detail(self,response):
        content = etree.HTML(response.text)
        item = NewsItem(language_id=self.language_id)
        item['pub_time'] = response.meta['pub_time']
        item['abstract'] = '\n'.join(response.meta['abstract'])
        item['images'] = content.xpath('//div[@itemprop="articleBody"]/table/tbody//tr/td/img[contains(@loading,"lazy")]/@src')
        if content.xpath('//div[@class="brcrum-title"]/span/a/text()'):
            item['category1'] = content.xpath('//div[@class="brcrum-title"]/span/a/text()')[0]
        else :item['category1'] = None
        body = content.xpath('//div[@itemprop="articleBody"]/p/text()')
        body.extend(content.xpath('//div[@itemprop="articleBody"]/p/span/text()'))
        body.extend(content.xpath('//div[@itemprop="articleBody"]/p/font/span/text()'))
        if len(item['abstract']) == 0: item['abstract'] = [body[0]]
        if body:
            abstract = [item['abstract']]
            item['body'] = '\n'.join(abstract+body)
        else :return
        if content.xpath('//div[@class="article-detail"]/h1/text()'):
            item['title'] = content.xpath('//div[@class="article-detail"]/h1/text()')[0].strip()
        else : return
        yield item


