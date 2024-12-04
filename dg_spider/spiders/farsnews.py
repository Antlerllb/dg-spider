


from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil

class FarsnewsSpider(BaseSpider):#author 梁皓然
    name = 'farsnews'
    allowed_domains = ['farsnews.ir']
    website_id = 2884
    language_id = 1876
    start_urls = ['https://www.farsnews.ir']
    author = '梁皓然'

    def parse(self, response):
        soup = BeautifulSoup(response.text,'html.parser')
        title_item = soup.select('.collapse.list-unstyled')[2:9:1]
        for i in title_item:
            catagory1 = i.select('a')[0].text
            test = i.select('a')[1].get('href')
            ca_url = 'https://www.farsnews.ir' + i.select('a')[0].get('href')
            start_url = response.url
            meta = {'category1':catagory1,'url':ca_url,'idx':2,'start_url':start_url}#idx标记下有一个应该取哪一个div
            yield Request(url = ca_url,callback= self.parse_page,meta = meta)

    def parse_page(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        flag = True
        #print(response.url)
        news_item = soup.select('.media.py-3.border-bottom.align-items-start')+soup.select('.top-post.py-3.text-left.d-flex')
        for i in news_item:
            news_time_item = (i.select('.publish-time.align-self-end.old-date')+i.select('.publish-time.align-self-end'))[0].get('datetime')
            dd = news_time_item.split()[0].split('/')[0]
            mm = news_time_item.split()[0].split('/')[1]
            yy = news_time_item.split()[0].split('/')[2]
            hh = news_time_item.split()[1].split(':')[0]
            min = news_time_item.split()[1].split(':')[1]
            ss = news_time_item.split()[1].split(':')[2]
            jud = news_time_item.split()[2]
            if (jud == 'PM' and int(hh)>12):
                temp = int(hh)
                temp += 12
                hh = str(temp)
            news_time = yy + '-' + '{:0>2}'.format(dd) + '-' + '{:0>2}'.format(mm) + ' ' + '{:0>2}'.format(
                hh) + ':' + '{:0>2}'.format(min) + ':' + '{:0>2}'.format(ss)
            #test = news_time
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(news_time) >= OldDateUtil.time:
                news_url = 'https://www.farsnews.ir'+ i.select('.d-flex.flex-column.h-100.justify-content-between')[0].get('href')
                #test1 = i.select('.title.d-block.mb-2')[0].text
                test2 = i.select('p')[0].text
                response.meta['title'] = i.select('.title.d-block.mb-2')[0].text
                response.meta['abstract'] = test2
                response.meta['pub_time'] = news_time
                yield Request(url = news_url,callback=self.parse_item,meta = response.meta)
            else:
                flag = False
                self.logger.info("时间截止")

        if flag:
            next_page_url = response.meta['url'] + '?p='+str(response.meta['idx'])
            response.meta['idx'] += 1
            yield Request(url = next_page_url,callback=self.parse_page,meta = response.meta)

        else:
            self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        # test = response.meta['category1']
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        article = soup.select('p')
        body = response.meta['category1'] +'\n' + article[0].text
        body = '\n'.join(
            [' '.join(content.text.replace('\xa0', '').replace('\n', '').strip().split()) for content in article if
             content.text.strip() != ''])
        item['body'] = body
        #testabs = response.meta['abstract'].strip()
        item['abstract'] = response.meta['abstract'].strip()
        item['pub_time'] = response.meta['pub_time']
        item['images'] = []
        if len(soup.select('img[itemprop="thumbnailUrl"]')) > 0:
            img = soup.select('img[itemprop="thumbnailUrl"]')[0].get('src')
            item['images'].append(img)
        if body:
            if len(article) == 1:
                body = response.meta['category1'] +'\n' + article[0].text
                item['body'] = body
            yield item