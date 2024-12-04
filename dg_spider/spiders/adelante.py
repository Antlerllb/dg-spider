import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class AdelanteSpider(BaseSpider):  # 类名重命名
    author = '刘雨鑫'
    name = 'adelante'  # name的重命名
    website_id = 1299  # id一定要填对！
    language_id = 2181  # id一定要填对！
    lan_num = 2
    start_urls = ['http://www.adelante.cu/index.php/es/', 'http://www.adelante.cu/index.php/en/']
    is_http = 1

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
            result += i
            if i != ss_list[-1]:
                result += ' '
        return result

    def parse(self, response):  # 主页，用于点进每个菜单
        li_list = response.xpath('/html/body/div[1]/div[1]/div[1]/nav/div[2]/ul/li[1]/following-sibling::li')
        for li in li_list:
            class_url = 'http://www.adelante.cu' + li.xpath('./a/@href').extract_first()
            yield scrapy.Request(class_url, callback=self.parse_page, meta={'class_url': class_url})

    def parse_page(self, response):  # 新闻列表页，用于点进每个新闻
        block = response.xpath('//div[@itemprop="blogPost"]')
        if len(block) == 0:
            block = response.xpath('//div[@class="item"]')
        for i in block:  # 可补：页码越界判断
            time_list = i.xpath('.//time[@itemprop="datePublished"]/@datetime')
            if len(time_list) == 0:
                time_list = i.xpath('./h3/text()').extract_first().split()
                if 'es' in response.meta['class_url']:
                    pub_time = f'{time_list[2]}-{str(OldDateUtil.ES_2181_DATE[time_list[1]]).zfill(2)}-{time_list[0]} 00:00:00'
                elif 'en' in response.meta['class_url']:
                    pub_time = f'{time_list[2]}-{str(OldDateUtil.EN_1866_DATE[time_list[1]]).zfill(2)}-{time_list[0]} 00:00:00'
            else:
                time_list = time_list.extract_first()
                detail_time = time_list.split('-')[2].split('T')[1]
                pub_time = f'{time_list[0:4]}-{time_list[5:7]}-{time_list[8:10]} ' + detail_time
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                return
            response.meta['pub_time'] = pub_time
            if len(i.xpath('.//img/@src').extract()) != 0:
                response.meta['image_first'] = 'http://www.adelante.cu/' + i.xpath('.//img/@src').extract_first()
            else:
                response.meta['image_first'] = ''
            url = i.xpath('.//h2[1]/a/@href').extract()
            if len(url) == 0:
                url = i.xpath('./h3/a/@href').extract()
            if len(url) != 0:
                detail_url = 'http://www.adelante.cu' + url[0]
                response.meta['category1'] = detail_url.split('/')[5]
                yield Request(
                    detail_url,
                    callback=self.parse_item, meta=response.meta
                    )
        next_url = response.xpath('//ul[@class="pagination-list"]//li[last()-1]/a/@href').extract_first()
        if next_url is not None:
            yield Request('http://www.adelante.cu' + next_url, callback=self.parse_page, meta=response.meta)

    def parse_item(self, response):  # 爬取新闻信息
        item = NewsItem(language_id=self.language_id)
        title_str = response.xpath('//div[@class="page-header"]/h2/text()').extract_first().replace(
            '\n', ''
            ).replace(
            '\t', ''
            )
        title = self.clear_none(title_str).replace('\t', '')
        body = ''
        if response.meta['image_first'] == '':
            images = []
        else:
            images = [response.meta['image_first']]
        images_main = response.xpath('//div[@class="articleBody"]//p//img/@src').extract()
        if len(images_main) != 0:
            for i in images_main:
                images.append('http://www.adelante.cu/' + i)
        tag = response.xpath('//div[@class="articleBody"]//p')
        for i in tag:
            p = ''
            for j in i.xpath('.//text()').extract():
                p += j.replace('\r', '').replace('\n', '')
            body += p + '\n'
        body = self.clear_none(self.clear(body.replace(' ', '')))
        if body == '':
            body = title
        body = self.clear_none(self.clear(body))
        abstract = body.split('\n')[0]
        item['title'] = title
        item['category1'] = response.meta['category1']
        item['images'] = images
        item['pub_time'] = response.meta['pub_time']
        if len(body.split('\n')) == 1:
            body = title + '\n' + body
        item['abstract'] = abstract
        if 'es' in response.meta['class_url']:
            self.language_id = 2181
        elif 'en' in response.meta['class_url']:
            self.language_id = 1866
        item['body'] = self.clear_none(body)
        yield item
