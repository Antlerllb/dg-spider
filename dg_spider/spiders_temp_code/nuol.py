import bs4, re

from dg_spider.items import NewsItem
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import scrapy



# check:魏芃枫 pass
class nuolSpider(BaseSpider):  # author：田宇甲 我喂自己袋盐 
    name, website_id, language_id, start_urls = 'nuol', 1652, 2005, ['https://www.nuol.edu.la/index.php/lo/nuol_news?start=1020']  # 一篇新闻的正文和翻页都在同一页

    def parse(self, response):
        soup, item = bs4.BeautifulSoup(response.text, 'html.parser'), NewsItem()
        for i in soup.find_all(class_=re.compile('items-row cols-1')):
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(i.select_one(' .published').time).split('datetime="')[1].split('"')[0].split('+')[0].replace('T', ' ')) >= int(OldDateUtil.time):
                item['pub_time'], item['title'], item['category1'], item['body'], item['abstract'], item['images']= str(i.select_one(' .published').time).split('datetime="')[1].split('"')[0].split('+')[0].replace('T', ' '), i.h2.text.strip('\n').strip(), 'ພາບບັນຍາກາດ', ('\n'.join(x.text for x in i.select(' .item-content p')) if i.select(' .item-content p') is not None else i.text.strip('\n').strip()), (i.select_one(' .item-content p').text if i.select_one(' .item-content p') is not None else i.text.strip('\n').strip()), ('https://www.nuol.edu.la'+i.figure.img['src'] if i.figure is not None else 'https://www.nuol.edu.la'+i.img['src'] if i.img is not None else None)
                yield item
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(i.select_one(' .published').time).split('datetime="')[1].split('"')[0].split('+')[0].replace('T', ' ')) >= int(OldDateUtil.time):  # 这里的time_为上面for循环的最后一个时间戳，用于下面翻页检索
            yield scrapy.http.request.Request(response.url.split('start=')[0]+'start='+str(int(response.url.split('start=')[1])+6))
