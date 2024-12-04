

from dg_spider.items import NewsItem
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy


'''
    Author：李旭明
    Date：2024.4.4
    Country：巴基斯坦
    Language：英语
    URL（原网站经历了重构）：https://pakistaneconomicnet.com----->https://pakeconet.com.pk/
'''


class PakistaneconomicSpider(BaseSpider):  # 类名重命名
    author = '李旭明'
    name = 'pakistaneconomic'  # name的重命名
    website_id = 2334  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    start_urls = ['https://pakistaneconomicnet.com']

    # 新闻首页解析
    def parse(self, response):
        # 获取新闻顶栏菜单
        menu_link = response.xpath('//ul[@id="menu-main"]/li[position()!=1 and position()!=2 and position()!=3]/a/@href').extract()
        # 进入菜单分类
        for category in menu_link:
            yield scrapy.Request(url=category, callback=self.parse_page)

    # 新闻列表页解析
    def parse_page(self, response):
        category = response.xpath('//h1[@class="archive-heading"]/span/text()').extract_first()
        # 获取该页新闻列表
        news_list = response.xpath('//section[@class="block-wrap block-grid mb-none"]//div[@class="content"]//h2[@class="is-title post-title"]/a/@href').extract()
        if news_list is None:
            return

        # 获取发布时间
        pub_time = []
        pub_time_judge = []
        pub_time_raw = response.xpath('//section[@class="block-wrap block-grid mb-none"]//div[@class="content"]//span[@class="date-link"]/time/@datetime').extract()
        for time in pub_time_raw:
            ymd = time[0:10]
            hms = time[11:19]
            pub_time.append(ymd + " " + hms)
            pub_time_judge.append(ymd)

        # 进入每则新闻
        for news in news_list:
            index = news_list.index(news)
            # 时间截止
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time_judge[index]) < OldDateUtil.time:
                return
            else:
                yield scrapy.Request(url=news, callback=self.parse_news, meta={"category1": category, "pub_time": pub_time[index]})

        # 翻页
        next_page = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse_page)

        # if 'page' not in response.url:
        #     next_page = response.url + 'page/2/'
        # else:
        #     last_slash_index = response.url.rfind("/")
        #     # 从0到最后一个斜杠之前搜索，找到倒数第二个斜杠
        #     second_last_slash_index = response.url.rfind("/", 0, last_slash_index)
        #     # 构造下一页url
        #     next_first_part = response.url[:second_last_slash_index+1]
        #     next_second_part = str(int(response.url[second_last_slash_index+1:last_slash_index])+1) + '/'
        #     next_page = next_first_part + next_second_part
        # yield scrapy.Request(url=next_page, callback=self.parse_page, meta={"category1": category})

    # 每则新闻内页面解析
    def parse_news(self, response):
        item = NewsItem(language_id=self.language_id)
        title = response.xpath('//h1[@class="is-title post-title"]/text()').extract_first()
        article_raw = response.xpath('//div[@class="post-content cf entry-content content-spacious"]/p/text()').extract()
        article = []
        # 移除&nbsp;，空格" "，错误的标点，以及单独一段的作者名
        for each in article_raw:
            if each != "&nbsp;" and each.strip() != "" and len(each) > 10:
                if "By" in each:
                    if "." in each:
                        article.append(each)
                else:
                    article.append(each)

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

        images = response.xpath('//div[@class="featured"]//img/@src').extract()
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
