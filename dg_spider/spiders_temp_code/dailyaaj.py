from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy



'''
    Author：李旭明
    Date：2024.03.28
    Country：巴基斯坦
    Language：乌尔都语
    URL：https://www.dailyaaj.com.pk/
'''


class DailyaajSpider(BaseSpider):  # 类名重命名
    author = '李旭明'
    name = 'dailyaaj'  # name的重命名
    website_id = 2317  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    start_urls = ['https://www.dailyaaj.com.pk/']

    # 新闻首页解析
    def parse(self, response):
        # 获取新闻顶栏菜单
        menu_link = response.xpath('//ul[@id="primary-menu"]/li[position()!=1 and position()!=13]/a/@href').extract()
        menu_text = response.xpath('//ul[@id="primary-menu"]/li[position()!=1 and position()!=13]/a/span/text()').extract()

        # 进入菜单分类
        for category in menu_link:
            index = menu_link.index(category)
            yield scrapy.Request(url=category, callback=self.parse_page, meta={"category1": menu_text[index]})

    # 新闻列表页解析
    def parse_page(self, response):
        # 获取该页新闻列表
        news_list = response.xpath('//div[@class="archive-entry-content"]/h4/a/@href').extract()
        if news_list is None:
            return

        # 获取发布时间
        pub_time = []
        pub_time_judge = []
        pub_time_raw = response.xpath('//time[@class="entry-date published"]/text()').extract()
        for time in pub_time_raw:
            year = time.split('\xa0')[2]
            month = str(OldDateUtil.UR_2238_DATE[time.split('\xa0')[1]])
            day = time.split('\xa0')[0].strip()
            pub_time.append(year + '-' + month + '-' + day + " 00:00:00")
            pub_time_judge.append(year + '-' + month + '-' + day)

        # 进入每则新闻
        for news in news_list:
            index = news_list.index(news)
            # 时间截止
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time_judge[index]) < OldDateUtil.time:
                return
            else:
                yield scrapy.Request(url=news, callback=self.parse_news, meta={"category1": response.meta["category1"], "pub_time": pub_time[index]})

        # 翻页
        next_page = response.xpath('//ul[@class="pagination"]/li/a[@rel="next"]/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse_page, meta={"category1": response.meta["category1"]})

    # 每则新闻内页面解析
    def parse_news(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.xpath('//h1[@class="entry-title"]/text()').extract_first()
        article = response.xpath('//div[@class ="entry-content"]//p//text()').extract()
        # 第一段中网页源码包含一些地点等标签，需要去掉该部分文字，文本太短则不认为是正文
        if len(article[0]) <= 15:
            article = article[1:]

        # 如果文章只有一段，标题作为摘要，将摘要和正文拼接
        if len(article) == 1:
            abstract = title
            body = abstract + '\n' + article[0]
        else:
            abstract = article[0]
            # 如果在摘要后正文只有一段，则将摘要和正文拼接，换行
            if len(article) == 2:
                body = '\n'.join(article)
            else:
                body = '\n'.join(article[1:])

        images = [response.xpath('//div[@class="post-header-image"]/img/@src').extract_first()]
        category1 = response.meta["category1"]
        pub_time = response.meta["pub_time"]

        item['title'] = title
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = images
        item['body'] = body
        item['category1'] = category1
        yield item
