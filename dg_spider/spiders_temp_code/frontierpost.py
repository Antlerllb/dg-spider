


from datetime import datetime, timedelta
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

'''
    Author：李旭明
    Date：2024.4.11
    Country：巴基斯坦
    Language：英语
    URL：https://thefrontierpost.com/
    Other：该网站以前爬过，导致数据库已有爬虫名thefrontierpost，重新拉取框架后仍不能使用该名字
'''


class FrontierpostSpider(BaseSpider):  # 类名重命名
    author = '李旭明'
    name = 'frontierpost'  # name的重命名
    website_id = 2311  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    proxy = "02"
    start_urls = ['https://thefrontierpost.com/']

    # 新闻首页解析
    def parse(self, response):
        # 获取新闻顶栏菜单
        menu_link = response.xpath('//div[@class="header-bottom-wrapper"]//nav//li/a[text()!="Home" and text('
                                   ')!="E-Paper" and text()!="News In Pictures" and text()!="About Us" and text('
                                   ')!="Advertise with Us" and text()!="Contact Us" and text('
                                   ')!="More"]/@href').extract()
        # 进入菜单分类
        for category in menu_link:
            yield scrapy.Request(url=category, callback=self.parse_page)

    # 新闻列表页解析
    def parse_page(self, response):
        category = response.xpath('//span[@class="meta-category"]/a/text()').extract_first()
        # 获取该页新闻列表
        news_list = response.xpath('//h2[@class="entry-title"]/a/@href').extract()
        if news_list is None:
            return

        # 获取发布时间
        current_time = datetime.now()
        pub_time_raw = response.xpath('//div[@class="meta-item date"]/span/text()').extract()
        pub_time = []
        pub_time_judge = []
        # 网站没有具体发布时间，需要计算发布时间
        for each in pub_time_raw:
            process_time_num = int(each.split(" ")[0])
            process_time_unit = each.split(" ")[1]
            if process_time_unit == "second" or process_time_unit == "seconds":
                pub_time.append((current_time - timedelta(seconds=process_time_num)).strftime("%Y-%m-%d %H:%M:%S"))
                pub_time_judge.append((current_time - timedelta(seconds=process_time_num)).strftime("%Y-%m-%d"))
            elif process_time_unit == "minute" or process_time_unit == "minutes":
                pub_time.append((current_time - timedelta(minutes=process_time_num)).strftime("%Y-%m-%d %H:%M:%S"))
                pub_time_judge.append((current_time - timedelta(minutes=process_time_num)).strftime("%Y-%m-%d"))
            elif process_time_unit == "hour" or process_time_unit == "hours":
                pub_time.append((current_time - timedelta(hours=process_time_num)).strftime("%Y-%m-%d %H:%M:%S"))
                pub_time_judge.append((current_time - timedelta(hours=process_time_num)).strftime("%Y-%m-%d"))
            elif process_time_unit == "day" or process_time_unit == "days":
                pub_time.append((current_time - timedelta(days=process_time_num)).strftime("%Y-%m-%d %H:%M:%S"))
                pub_time_judge.append((current_time - timedelta(days=process_time_num)).strftime("%Y-%m-%d"))
            elif process_time_unit == "week" or process_time_unit == "weeks":
                pub_time.append((current_time - timedelta(weeks=process_time_num)).strftime("%Y-%m-%d %H:%M:%S"))
                pub_time_judge.append((current_time - timedelta(weeks=process_time_num)).strftime("%Y-%m-%d"))
            elif process_time_unit == "month" or process_time_unit == "months":
                process_time_num = process_time_num * 4
                pub_time.append((current_time - timedelta(weeks=process_time_num)).strftime("%Y-%m-%d %H:%M:%S"))
                pub_time_judge.append((current_time - timedelta(weeks=process_time_num)).strftime("%Y-%m-%d"))
            elif process_time_unit == "year" or process_time_unit == "years":
                process_time_num = process_time_num * 4 * 12
                pub_time.append((current_time - timedelta(weeks=process_time_num)).strftime("%Y-%m-%d %H:%M:%S"))
                pub_time_judge.append((current_time - timedelta(weeks=process_time_num)).strftime("%Y-%m-%d"))
            else:
                # 如果无法计算，则当作是爬取当天发表的
                pub_time.append(current_time.strftime("%Y-%m-%d %H:%M:%S"))
                pub_time_judge.append(current_time.strftime("%Y-%m-%d"))

        # 进入每则新闻
        for news in news_list:
            index = news_list.index(news)
            # 时间截止
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time_judge[index]) < OldDateUtil.time:
                return
            else:
                yield scrapy.Request(url=news, callback=self.parse_news, meta={"category1": category, "pub_time": pub_time[index]})

        # 翻页
        next_page = response.xpath('//nav[@id="vce-pagination"]/a/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse_page)

    # 每则新闻内页面解析
    def parse_news(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.xpath('//h1[@class="entry-title"]//text()').extract_first()
        # 某些页面新闻标题出错，为空
        if title is None:
            return
        article_raw = response.xpath('//div[@class="entry-content"]/p/text()').extract()
        article = []
        # 移除&nbsp;，空格" "，错误的标点，以及单独一段的作者名
        for each in article_raw:
            if each != "&nbsp;" and each.strip() != "" and len(each) > 20:
                if each.strip()[-1] != ".":
                    continue
                else:
                    article.append(each.strip())

        # 如果文章只有一段，标题作为摘要，将摘要和正文拼接
        if len(article) == 1:
            abstract = title
            body = abstract + '\n' + article[0]
        else:
            abstract = article[0]
            # 如果在摘要后正文只有一段，将摘要和正文拼接，换行
            if len(article) == 2:
                body = '\n'.join(article)
            else:
                body = '\n'.join(article[1:])

        images = response.xpath('//main//div[@class="meta-image"]/img/@src').extract()
        category1 = response.meta["category1"]
        pub_time = response.meta["pub_time"]
        item['title'] = title
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = images
        item['body'] = body
        item['category1'] = category1
        item['language_id'] = 1866
        yield item
