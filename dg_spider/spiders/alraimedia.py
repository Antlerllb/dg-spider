import re



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
import scrapy
import time
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil




class AlraimediaSpider(BaseSpider):
    name = 'alraimedia'
    website_id = 2605
    language_id = 1748
    author = '何乐轩'
    start_urls = ['https://www.alraimedia.com/']
    base_url = 'https://www.alraimedia.com/'

    
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for category in soup.select('.sectionMenu .menu-li ')[5:-2]:
            response.meta['category1']=category.select_one('a').text.strip()
            in_page_url=category.select_one('a').get('href')
            yield Request(url=in_page_url, callback=self.parse_menu,meta=response.meta)
    
    def parse_menu(self,response):
        soup = BeautifulSoup(response.text, 'html.parser')
        if len(soup.select(".paddingDefault .barInfo a"))!=0:
            url=soup.select_one(".paddingDefault .barInfo a")['href']
            response.meta['this_url']=url
            yield Request(url=url, callback=self.parse_menu2,meta=response.meta)
        # else:
        #     return
    
    def parse_menu2(self, response):#新闻类别
        soup = BeautifulSoup(response.text, 'html.parser')     
        for news in soup.select('.container .row .col-sm-3'):
            if 'no-image' in news.select_one('a div img')['src']:
                return
            time_list=news.select_one('a div img')['src'].split("/")[-4:-1]
            last_time = f'{time_list[0]}-{time_list[1]}-{time_list[2]} 00:00:00' #2022-10-11 00:00:00
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(last_time) < OldDateUtil.time:
                return
            response.meta['pub_time'] = last_time
            next_web=news.select_one('a')['href']
            yield Request(url=next_web, callback=self.parse_item, meta=response.meta) 
            
        page_num=int(soup.select('.pagination .pager li')[-2].select_one('a').text.strip())
        cur=int(soup.select_one('.pagination .pager .active a').text.strip())
        if cur<page_num:
            url=response.meta['this_url']+'?pgno='+str(cur+1)
            yield Request(url=url, callback=self.parse_menu2,meta=response.meta)
                           
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        
        # the_time=soup.select_one('.col-md-10 .relative .article-date').text.strip().split(' ')
        # if the_time[1]=='يوليو':
        #         the_time[1]='جويلية'
        # elif the_time[1]=='أبريل':
        #     the_time[1]='إبريل'
        # last_time=f'{the_time[2]}-{OldDateUtil.AR_1748_DATE[the_time[1]]}-{the_time[0]} 00:00:00' #2022-10-11 00:00:00
        
        # if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(last_time) < OldDateUtil.time:
        #     return
        item['pub_time'] = response.meta['pub_time']
        # item['pub_time'] = last_time
        item['title'] = soup.select_one('.col-md-10 .article-title').text.strip()
        item['category1']=response.meta['category1']
        imgArr=[]
        body=[]
        item['body'] = ' '
        item['abstract']=' '
        if soup.select_one('.col-md-10 .relative div img') is not None:
            img=soup.select_one('.col-md-10 .relative div img')['src']
            if 'https://cdn4.premiumread.com' not in img:
                if 'https://www.alraimedia.com' not in img:
                    imgArr.append('https://www.alraimedia.com'+img)
                else:
                    imgArr.append(img)
        
        for p in soup.select('.col-md-10 .relative .article-desc'):#可能图片在每段文字中
            if p.text is not None or p is not None:
                for b in p.text.strip().split('\n'):
                    body.append(b)
        item['images'] = [img for img in imgArr]
        # b="\n".join('%s' %a for a in body)
        b="\n".join(body)
        item['body'] = b
        item['abstract'] = item['body'].split('\n')[0]
        if item['body'].split('\n')[0]=='' or body=='':#没有正文就丢弃
            return
        return item  


