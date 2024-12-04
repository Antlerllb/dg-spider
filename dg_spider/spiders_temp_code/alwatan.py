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
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


class AlwatanSpider(BaseSpider):
    name = 'alwatan'
    website_id = 2614
    language_id = 1748
    author = '何乐轩'
    start_urls = ['https://alwatan.com/']
    base_url = 'https://alwatan.com/'
    
    
    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for category in soup.select('.container .container .menu li')[1:]:
            if category.select_one('a').get('href')=='#':
                return
            response.meta['category1']=category.select_one('a').text.strip()
            in_page_url=category.select_one('a').get('href')
            response.meta['this_url']=in_page_url
            if in_page_url!='https://alwatan.com/section/caricature%e2%80%8e':
                yield Request(url=in_page_url, callback=self.parse_menu,meta=response.meta)
        
    def parse_menu(self, response):#新闻类别
        soup = BeautifulSoup(response.text, 'html.parser')     
        for news in soup.select('.post-listing>article'):
            time_list=news.select_one('p>span').text.strip().split(' ')
            time_list[1]=time_list[1].split('،')[0]
            if time_list[1]=='يوليو':
                time_list[1]='جويلية'
            elif time_list[1]=='أبريل':
                time_list[1]='إبريل'
            last_time = f'{time_list[2]}-{str(OldDateUtil.AR_1748_DATE[time_list[1]]).zfill(2)}-{time_list[0]} 00:00:00' #2022-10-11 00:00:00
            
            if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(last_time) < OldDateUtil.time:
                return
            response.meta['pub_time'] = last_time
            response.meta['abstract'] = news.select_one('.entry p').text.strip()
            next_web=news.select_one('.post-title a').get('href')
            # response.meta['num']+=1
            yield Request(url=next_web, callback=self.parse_item, meta=response.meta)
         
        page_num=int(''.join(soup.select_one('.pagination .pages').text.strip().split(' ')[3].split('٬')))
        cur=int(soup.select_one('.pagination .current').text.strip())
        if cur<page_num:
            url=response.meta['this_url']+'/page/'+str(cur+1)
            yield Request(url=url, callback=self.parse_menu,meta=response.meta)   
        # url=''
        # for i in soup.select('.pagination a'):
        #     if i.text.strip()=='»':
        #         url=i['href']
        #         break
        # if url !='':
        #     yield Request(url=url, callback=self.parse_menu,meta=response.meta)
                           
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)

        item['title'] = soup.select_one('.content .post-inner .post-title').text.strip()
        item['pub_time'] = response.meta['pub_time']
        item['category1']=response.meta['category1']
        imgArr=[]
        body=[]
        item['body'] = ' '
        item['abstract']=' '
        if soup.select_one('.content .single-post-thumb img') is not None:
            img=soup.select_one('.content .single-post-thumb img')['src'].split('//')
            imgArr.append(img[0]+'//www.'+img[1])
        for p in soup.select('.content .entry p'):#可能图片在每段文字中
            if p.text is not None or p is not None:
                # b=p.text.strip().split('\n')
                for b in p.text.strip().split('\n'):
                    body.append(b)
            else:
                body.append(response.meta['abstract'])
        for td in soup.select('.entry td'):
            if td.text is not None or td is not None:
                # b=p.text.strip().split('\n')
                for b in td.text.strip().split('\n'):
                    body.append(b)
            else:
                body.append(response.meta['abstract'])
            
        if len(soup.select('.content .entry p'))==0 and len(soup.select('.entry td'))==0:#没有正文就丢弃
            return
    
        item['images'] = [img for img in imgArr]
        # b="\n".join('%s' %a for a in body)
        b="\n".join(body)
        if len(body)<=1:
            b='\n'.join([response.meta['abstract'],body[0]])
        item['body'] = b
        # item['abstract'] = item['body'].split('\n')[0]
        item['abstract'] = response.meta['abstract']
        return item



