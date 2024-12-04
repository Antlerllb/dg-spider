


import re
import json
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

'''
    Author：李旭明
    Date：2024.4.25
    Country：巴基斯坦
    Language：英语
    URL：https://arynews.tv/
'''


class ArynewsSpider(BaseSpider):  # 类名重命名
    author = '李旭明'
    name = 'arynews'  # name的重命名
    website_id = 2294  # id一定要填对！
    language_id = 2238  # id一定要填对！
    lan_num = 1
    start_urls = ['https://arynews.tv/']
    td_magic_token = ''  # 网页post所需的随机数值
    time_judge = True  # 时间截止标志

    # 新闻首页解析
    def parse(self, response):
        # 获取新闻顶栏菜单
        category_link = response.xpath('//ul[@id="menu-main-menu-2"]/li[position()!=1 and position()!=5 and position()!=7 and position()!=12]/a/@href').extract()

        # 获取翻页的post必要参数td_magic_token，获取不到则无法翻页爬取
        if "tdBlockNonce" in response.text:
            # 使用正则表达式提取变量值
            nonce = r'tdBlockNonce.*"(.*)";'
            match = re.search(nonce, response.text)
            if match:
                ArynewsSpider.td_magic_token = match.group(1)
            else:
                return
        else:
            return

        # 进入菜单分类
        for category in category_link:
            yield scrapy.Request(url=category, callback=self.parse_page)

    # 第一页新闻列表页解析
    def parse_page(self, response):
        # 获取菜单名
        category = response.xpath('//h1[@class="tdb-title-text"]/text()').extract_first()
        # 获取该页新闻列表
        news_list = response.xpath('//div[@class="td-module-meta-info"]/h3[@class="entry-title td-module-title"]/a/@href').extract()
        if news_list is None:
            return

        # 获取图片
        image_list = response.xpath('//div[@class="td-image-container"]//span/@data-img-url').extract()

        # 进入每则新闻
        for news in news_list:
            index = news_list.index(news)
            # 时间截止
            if not ArynewsSpider.time_judge:
                return
            else:
                yield scrapy.Request(url=news, callback=self.parse_news, meta={"category1": category, "image": [image_list[index]]})

        # 翻页
        next_page_link = 'https://arynews.tv/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=12.6.2'

        # 设置category_id
        if category == "Pakistan":
            category_id = "51"
        if category == "International":
            category_id = "11"
        if category == "Business":
            category_id = "24"
        if category == "Science & Technology":
            category_id = "22"
        if category == "Lifestyle":
            category_id = "116"
        if category == "Health":
            category_id = "740"
        if category == "Offbeat":
            category_id = "118"
        if category == "Latest Blogs":
            category_id = "513381"

        # 从网络负载中确认所必需的元素后，设置post的formdata
        post_data = {
            "td_current_page": "2",
            'td_magic_token': ArynewsSpider.td_magic_token,  # 必要，且每天会变化，要每天自动获取
            'block_type': 'tdb_loop',  # 必要
            'action': 'td_ajax_block',  # 关键
            'td_atts': '{"modules_category":"above",'
                       '"show_excerpt":"eyJwb3J0cmFpdCI6Im5vbmUiLCJhbGwiOiJub25lIn0=",'
                       '"show_btn":"none",'
                       '"hide_audio":"yes",'
                       '"show_cat":"none",'
                       '"show_author":"none",'
                       '"show_com":"none",'
                       '"show_review":"none",'
                       '"show_date":"none",'
                       '"ad_loop":"JTNDc2NyaXB0JTIwYXN5bmMlMjBzcmMlM0QlMjJodHRwcyUzQSUyRiUyRnBhZ2VhZDIuZ29vZ2xlc3luZGljYXRpb24uY29tJTJGcGFnZWFkJTJGanMlMkZhZHNieWdvb2dsZS5qcyUzRmNsaWVudCUzRGNhLXB1Yi00MjA0ODYxNDY1Njk0NzQ5JTIyJTBBJTIwJTIwJTIwJTIwJTIwY3Jvc3NvcmlnaW4lM0QlMjJhbm9ueW1vdXMlMjIlM0UlM0MlMkZzY3JpcHQlM0UlMEElM0NpbnMlMjBjbGFzcyUzRCUyMmFkc2J5Z29vZ2xlJTIyJTBBJTIwJTIwJTIwJTIwJTIwc3R5bGUlM0QlMjJkaXNwbGF5JTNBYmxvY2slMjIlMEElMjAlMjAlMjAlMjAlMjBkYXRhLWFkLWZvcm1hdCUzRCUyMmZsdWlkJTIyJTBBJTIwJTIwJTIwJTIwJTIwZGF0YS1hZC1sYXlvdXQta2V5JTNEJTIyLWgwJTJCZCUyQjVjLTktM2UlMjIlMEElMjAlMjAlMjAlMjAlMjBkYXRhLWFkLWNsaWVudCUzRCUyMmNhLXB1Yi00MjA0ODYxNDY1Njk0NzQ5JTIyJTBBJTIwJTIwJTIwJTIwJTIwZGF0YS1hZC1zbG90JTNEJTIyMzg3MTkzMzgwOSUyMiUzRSUzQyUyRmlucyUzRSUwQSUzQ3NjcmlwdCUzRSUwQSUyMCUyMCUyMCUyMCUyMChhZHNieWdvb2dsZSUyMCUzRCUyMHdpbmRvdy5hZHNieWdvb2dsZSUyMCU3QyU3QyUyMCU1QiU1RCkucHVzaCglN0IlN0QpJTNCJTBBJTNDJTJGc2NyaXB0JTNF",'
                       '"ad_loop_repeat":"6",'
                       '"category_id":' + category_id + ','  # 控制目录
                       '"mc1_tl":"",'
                       '"mc1_title_tag":"",'
                       '"mc1_el":"",'
                       '"open_in_new_window":"",'
                       '"image_size":"",'
                       '"hide_image":"",'
                       '"show_favourites":"",'
                       '"modules_extra_cat":"",'
                       '"author_photo":"",'
                       '"show_modified_date":"",'
                       '"time_ago":"",'
                       '"time_ago_add_txt":"ago",'
                       '"time_ago_txt_pos":"",'
                       '"excerpt_middle":"",'
                       '"btn_title":"",'
                       '"ad_loop_title":"- Advertisement -",'
                       '"ad_loop_disable":""}'
        }
        # post翻页
        yield scrapy.FormRequest(url=next_page_link, formdata=post_data, callback=self.parse_next_page, meta={"post_data": post_data, "category1": category})

    # 翻页后新闻列表页解析
    def parse_next_page(self, response):
        # 获取响应的文本内容
        body = response.text
        # 响应返回无文本则翻页结束
        if body == '':
            return
        # 将json格式数据转换为python字典
        json_data = json.loads(body)
        # 响应返回无所需数据则翻页结束
        if 'td_data' in json_data.keys():
            image_list = []
            html_content = json_data['td_data']
            soup = BeautifulSoup(html_content, 'html.parser')
            # 使用CSS选择器查找所有匹配的a标签，用于获取翻页后新闻的url
            a_tags = soup.select('h3.entry-title.td-module-title > a')
            # 响应返回无所需数据则翻页结束
            if a_tags:
                # 使用CSS选择器查找所有匹配的style标签，用于获取翻页后新闻的图片
                image = r'background-image:.*url\((.*?)\)'
                style_tags = soup.select('a > style')
                # 获取新闻图像url
                for each in style_tags:
                    match = re.search(image, each.string)
                    image_url = match.group(1)
                    image_list.append(image_url)
                # 获取每个a标签的href属性
                hrefs = [a['href'] for a in a_tags]
                # 翻页后每则新闻的爬取
                for news in hrefs:
                    index = hrefs.index(news)
                    # 时间截止
                    if not ArynewsSpider.time_judge:
                        return
                    else:
                        yield scrapy.Request(url=news, callback=self.parse_news, meta={"category1": response.meta["category1"], "image": [image_list[index]]})
            else:
                return
        else:
            return

        # 时间截止
        if not ArynewsSpider.time_judge:
            return
        # 继续翻页
        next_page_link = 'https://arynews.tv/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=12.6.2'
        post_data = response.meta["post_data"]
        post_data["td_current_page"] = str(int(post_data["td_current_page"]) + 1)
        yield scrapy.FormRequest(url=next_page_link, formdata=post_data, callback=self.parse_next_page, meta={"post_data": post_data, "category1": response.meta["category1"]})

    # 每则新闻内页面解析
    def parse_news(self, response):
        item = NewsItem(language_id=self.language_id)
        pub_time_raw = response.xpath('//div[@class="tdb-block-inner td-fix-index"]/time/@datetime').extract_first()
        if pub_time_raw is None:
            return
        ymd = pub_time_raw[0:10]
        hms = pub_time_raw[11:19]
        pub_time = ymd + " " + hms
        # 时间截止
        if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time) < OldDateUtil.time:
            ArynewsSpider.time_judge = False
            return

        title = response.xpath('//h1[@class="tdb-title-text"]/text()').extract_first()
        # abstract_raw和abstract记录文章第一段
        abstract_raw = response.xpath('//div[@class="tdb-block-inner td-fix-index"]//p[1]//text()').extract()
        if not abstract_raw:
            abstract_raw = response.xpath('//div[@class="tdb-block-inner td-fix-index"]//ul[1]//text()').extract()
        abstract = ''.join(abstract_raw).strip()
        if not abstract:
            abstract = title

        # article_raw和article记录文章第二段往后的段落
        article_raw = response.xpath('//div[@class="tdb-block-inner td-fix-index"]//p//text()').extract()
        if article_raw[0].strip() == abstract:
            article_raw.remove(article_raw[0])
        article = []
        # 移除&nbsp;，空格" "，错误的标点，以及单独一段的作者名
        for each in article_raw:
            if each != "&nbsp;" and each.strip() != "" and len(each) > 20:
                article.append(each.strip())

        if article:
            # 如果在摘要后正文只有一段，将摘要和正文拼接，换行
            if len(article) == 1:
                body = abstract + '\n' + article[0]
            else:
                body = '\n'.join(article)
        # 如果文章只有一段，标题作为摘要，将摘要和正文拼接
        else:
            temp = abstract
            abstract = title
            body = abstract + '\n' + temp

        images = response.meta["image"]
        category1 = response.meta["category1"]
        item['title'] = title
        item['abstract'] = abstract
        item['pub_time'] = pub_time
        item['images'] = images
        item['body'] = body
        item['category1'] = category1
        item['language_id'] = 1866
        yield item

