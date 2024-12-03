# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # Spider
    language_id = scrapy.Field(serializer=int)
    pub_time = scrapy.Field(serializer=str)  # 文章发布时间   格式为："%Y-%m-%d %H:%M:%S"
    abstract = scrapy.Field(serializer=str)  # 文章摘要   若没有则默认为文章第一句话
    body = scrapy.Field(serializer=str)  # 文章内容   需要作为一个完整的字符串存入
    category1 = scrapy.Field(serializer=str)  # 一级分类
    category2 = scrapy.Field(serializer=str)  # 二级分类
    title = scrapy.Field(serializer=str)  # 文章标题

    # Spider+ItemPipeline
    images = scrapy.Field()  # body中的图片链接url   要求是字符串的list，如：["url1","url2"...]

    # ItemPipeline
    website_id = scrapy.Field()
    md5 = scrapy.Field()
    cole_time = scrapy.Field()

    # ItemMiddleware
    request_url = scrapy.Field()
    response_url = scrapy.Field()
