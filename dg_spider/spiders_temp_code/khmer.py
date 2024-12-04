



import re
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


class KhmerSpider(BaseSpider):
    author = '阮博文'
    website_id = 2688
    language_id = 2275
    lan_num = 1
    name = "khmer"
    allowed_domains = ["khmer7news.com"]
    start_urls = ["https://khmer7news.com"]



    month_map = {
        "មករា": "01",  # January
        "កុម្ភៈ": "02",  # February
        "មិនា": "03",  # March
        "មីនា": "03",
        "មេសា": "04",  # April
        "ឧសភា": "05",  # May
        "មិថុនា": "06",  # June
        "កក្កដា": "07",  # July
        "សីហា": "08",  # August
        "កញ្ញា": "09",  # September
        "តុលា": "10",  # October
        "វិច្ឆិកា": "11",  # November
        "ខែធ្នូ": "12",  # December
        "ធ្នូ": "12"
    }

    def convert(self, time, period):
        hour, minute = time.split(':')
        hour = int(hour)
        minute = int(minute)
        # 根据 AM/PM 转换小时
        if period == 'ព្រឹក' and hour == 12:
            hour = 0
        elif period == 'ល្ងាច' and hour != 12:
            hour += 12
        # 格式化并返回 24 小时制的时间字符串
        return "%02d:%02d" % (hour, minute)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self, response):

        node_list = response.xpath('//*[@id="tie-widget-categories-2"]/ul/li')
        for node in node_list:  ##url_filter
            url = node.xpath('./a/@href')[0].extract()
            yield scrapy.Request(url=url, callback=self.parse_item)

    def parse_item(self, response):
        category_1 = response.xpath('//*[@id="content"]/div/div/header/h1/text()')[0].extract()
        response.meta['category1'] = category_1
        notes = response.xpath('//*[@id="content"]/div/div/div[1]/div/div/ul/li')
        for item in notes:
            images = []
            if item.xpath('./a/img/@src'):
                image = item.xpath('./a/img/@src')[0].extract()
                if image.startswith(("https://", "http://")):
                    images.append(image)
            else:
                return
            title = item.xpath('./a/@title')[0].extract().strip().replace('\u200b', '')
            pub_time = item.xpath('./div/span[2]/span[2]/text()')[0].extract()
            pub_time = pub_time.split(',')[1].strip()
            match = re.search(r'(\d{1,2})\s+([^\s\d]+)\s+(\d{4})\s+(\d{1,2}:\d{2})\s+([^\s]+)', pub_time)
            if match:
                day, month, year, time, period = match.groups()
                time = self.convert(time, period)
                month = self.month_map.get(month)
                pub_time = f"{year}-{month}-{int(day):02} {time}:00"

                if OldDateUtil.time is None or OldDateUtil.time < OldDateUtil.str_datetime_to_timestamp(pub_time):
                    response.meta['pub_time'] = pub_time
                    response.meta['images'] = images
                    response.meta['title'] = title
                    news_url = item.xpath('./div/a/@href')[0].extract()
                    yield scrapy.Request(url=news_url, callback=self.parse_detail, meta=response.meta)
                else:
                    return

        tmp = response.xpath('//*[@id="content"]/div/div/div[2]/div/span[2]/a/@href')
        if len(tmp) != 0:
            next_url = tmp[0].extract()
            yield scrapy.Request(url=next_url, callback=self.parse_item)

    def parse_detail(self, response):
        item = NewsItem(language_id=self.language_id)
        images = response.meta['images']
        image_list = response.xpath('//*[@id="the-post"]/div[2]/p/img/@src')
        if image_list:
            # 遍历得到的图像列表
            for img in image_list:
                url = img.extract()
                if url.startswith(("https://", "http://")):
                    images.append(url)
        body_paragraphs = response.xpath('//*[@id="the-post"]/div[2]/p/text()').getall()
        body_paragraphs = [para.replace('\u200b', '').replace('\n', '').replace('\r', '') for para in
                           body_paragraphs if para.strip()]
        body_paragraphs = [para.strip() for para in body_paragraphs]
        body = '\n'.join(body_paragraphs)

        first_sentence = body_paragraphs[0].split('។')[0] if '។' in body_paragraphs[0] else body_paragraphs[0].split()[0]
        if len(body_paragraphs) == 1:
            body = first_sentence+'\n'+body
        item['pub_time'] = response.meta['pub_time']
        item['images'] = images
        item['abstract'] = first_sentence
        item['body'] = body
        item['category1'] = response.meta['category1'] if 'category1' in response.meta.keys() else 'none'
        item['title'] = response.meta['title']
        # print(item)
        yield item




