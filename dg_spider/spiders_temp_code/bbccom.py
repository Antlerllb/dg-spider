import scrapy
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


from datetime import datetime
from dg_spider.items import NewsItem
import scrapy  
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy



class BbccomSpider(BaseSpider):
    author = '吴雨奔'
    website_id = 2325  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    name = "bbccom"
    allowed_domains = ["www.bbc.com"]
    start_urls = ["https://www.bbc.com/urdu"]
    proxy = '02'

    # 乌尔都语月份到公历月份的映射
    urdu_month_mapping = {
        'جنوری': '01',
        'فروری': '02',
        'مار چ': '03',
        'اپريل': '04',
        'مئ': '05',
        'جون': '06',
        'جولائی': '07',
        'اگست': '08',
        'ستمبر': '09',
        'اکتوبر': '10',
        'نومبر': '11',
        'دسمبر': '12'
    }

    @staticmethod
    def convert_urdu_date(urdu_date):
        # 分解乌尔都语日期格式
        parts = urdu_date.split()
        if len(parts) == 3:
            year = parts[0]
            month_name = parts[1]
            day = parts[2]
        else:
            year = parts[0]
            month_name = parts[1] + ' ' + parts[2]
            day = parts[3]
        # 根据映射获取月份数字
        month = BbccomSpider.urdu_month_mapping[month_name]

        # 构造标准日期格式
        formatted_date = f"{year}-{day}-{month}"

        # 使用datetime来验证和格式化日期
        valid_date = datetime.strptime(formatted_date, "%d-%Y-%m")
        return valid_date.strftime("%Y-%m-%d 00:00:00")

    def parse(self, response):
        column_list = response.xpath('//*[@id="main-wrapper"]/header/nav/div/div[1]/div/ul/li/a')
        for num, column in enumerate(column_list):
            if (num != 0):
                category1 = column.xpath('./text()').extract_first()
                column_link = response.urljoin(column.xpath('./@href').extract_first())
                yield scrapy.Request(
                    url=column_link,
                    callback=self.parse_column,
                    meta={'category1': category1}
                )

    def parse_column(self, response):
        category1 = response.meta['category1']
        news_list = response.xpath('//h2')
        for news in news_list:
            link = news.xpath('./a/@href').extract_first()
            pub_time = news.xpath('./../time/text()').extract_first()
            if pub_time is not None:
                if 'گھنٹہ قبل' in pub_time or 'گھنٹے' in pub_time or 'منٹ' in pub_time:
                    now = datetime.now()
                    pub_time = now.strftime("%Y-%m-%d 00:00:00")
                else:
                    pub_time = BbccomSpider.convert_urdu_date(pub_time)

                if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
                    continue
                else:
                    item = {}
                    item['pub_time'] = pub_time
                    item['category1'] = category1
                    title = news.xpath('./a/text()').extract_first()

                    if title is not None and title != '' :
                        item['abstract'] = title
                        item['title'] = title
                        yield scrapy.Request(
                            url=link,
                            callback=self.parse_news,
                            meta={'item': item}
                        )

        # 翻页按钮：>
        part_url = response.xpath('//a[@aria-labelledby="pagination-next-page"]/@href').extract_first()
        # print(f'当前页面：{part_url}')
        # 判断终止条件
        if part_url != '':
            # 最后一页为：javascript:void(0)
            # 符合条件不停地翻页
            next_url = response.urljoin(part_url)
            # 构建请求对象并且返回给引擎
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_column,
                meta={'category1': category1}
            )

    def parse_news(self, response):
        item = NewsItem(response.meta['item'])
        article = response.xpath('//main/div[@dir="rtl"]//text()').extract()
        article[:] = article[2:]
        if len(article) > 1:
            content = "\n".join(article)
        else:
            content = "\n" + item['title'] + "\n".join(article)
        item['body'] = content
        images = response.xpath('//main//img/@src').extract()
        if images == None or images == '':
            item['images'] = []
        else:
            item['images'] = images
        yield item
