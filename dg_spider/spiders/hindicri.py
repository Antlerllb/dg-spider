# encoding: utf-8

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author : 钟钧仰
class HindiCriSpider(BaseSpider):
    name = 'hindicri'
    website_id = 2116
    language_id = 1930
    start_urls = ['https://hindi.cri.cn/']

    def parse(self, response):
        menu_list_cate1 = ['न्यूज़','वीडियो','टिप्पणी','तिब्बत']
        # menu_list_cate2 = []
        news = ['https://hindi.cri.cn/news/index.shtml?spm=C78358.PnHys1Qm6H0a.E66gZbvbJIdV.4','https://hindi.cri.cn/2022/08/16/ARTIeylZEvaxsWce1iaCFcY3220816.shtml?spm=C78358.POGuiU27vpyG.Ew20sY4WrVvr.10','https://hindi.cri.cn/comment/index.shtml?spm=C78358.PWWe0bsRpwDK.E66gZbvbJIdV.7','https://hindi.cri.cn/special/chinatibet/index.shtml?spm=C78358.Pk7al7VNmRpb.E66gZbvbJIdV.8']
        for i in range(0, 4):
            # response.meta['category2'] = menu_list_cate2[i]
            response.meta['category1'] = menu_list_cate1[i]
            response.meta['url'] = news[i]
            yield Request(url=news[i], callback=self.parse_category, meta=response.meta)
            # print(news[i])
    def parse_category(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        if response.meta['category1']=='न्यूज़':
            menu = soup.select('#contentELMTAIO7hntb3OeJRonP6fSj220418 > ul > li')
            for i in menu:
                response.meta['category2']='चीन'
                news_url = (i.select_one('a').get('href'))
                # print(news_url)
                response.meta['title'] =(i.select_one(' a > div.right > div.title').text)
                if news_url.find('http') == -1:
                    if news_url[1] == '/':
                        urls = 'https:' + news_url
                    else:
                        urls = 'https://hindi.cri.cn' + news_url
                else:
                    urls = news_url
                if news_url.find('.cri.cn') != -1:
                    news_url = news_url[news_url.find('.cri.cn') + 7:]
                if news_url[5] == '/' or news_url[5] == '-':
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[6:8] + '-' + news_url[9:11] + ' 00:00:00'
                else:
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[5:7] + '-' + news_url[7:9] + ' 00:00:00'
                if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield Request(url=urls, callback=self.parse_item, meta=response.meta)
            menu2 = soup.select('#contentELMTw20sY4WrVvrzqqRTGvy3220418 > ul > li')
            for i in menu2:
                news_url = (i.select_one('a').get('href'))
                response.meta['category2']='दक्षिण एशिया'
                response.meta['title'] = (i.select_one(' a > div.right > div.title').text)
                if news_url.find('http') == -1:
                    if news_url[1] == '/':
                        urls = 'https:' + news_url
                    else:
                        urls = 'https://hindi.cri.cn' + news_url
                else:
                    urls = news_url
                if news_url.find('.cri.cn') != -1:
                    news_url = news_url[news_url.find('.cri.cn') + 7:]
                if news_url[5] == '/' or news_url[5] == '-':
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[6:8] + '-' + news_url[9:11] + ' 00:00:00'
                else:
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[5:7] + '-' + news_url[7:9] + ' 00:00:00'
                if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield Request(url=urls, callback=self.parse_item, meta=response.meta)
            menu3 = soup.select('#contentELMTrwtlnqeme1zEgZ04J739220418 > ul > li')
            for i in menu3:
                news_url = (i.select_one('a').get('href'))
                response.meta['category2']='विश्व'
                response.meta['title'] = i.select_one(' a > div.right > div.title').text
                if news_url.find('http') == -1:
                    if news_url[1] == '/':
                        urls = 'https:' + news_url
                    else:
                        urls = 'https://hindi.cri.cn' + news_url
                else:
                    urls = news_url
                if news_url.find('.cri.cn') != -1:
                    news_url = news_url[news_url.find('.cri.cn') + 7:]
                if news_url[5] == '/' or news_url[5] == '-':
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[6:8] + '-' + news_url[9:11] + ' 00:00:00'
                else:
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[5:7] + '-' + news_url[7:9] + ' 00:00:00'
                if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield Request(url=urls, callback=self.parse_item, meta=response.meta)
        elif response.meta['category1']=='वीडियो':
            menu = soup.select('#contentELMTg5qsSF9QsAWObzuAnVy9220418 > ul > li')
            for i in menu:
                response.meta['category2'] = 'चाइना लाइफ'
                news_url = (i.select_one('a').get('href'))
                response.meta['title'] =(i.select_one('a > div.subtitle').text)
                if news_url.find('http') == -1:
                    if news_url[1] == '/':
                        urls = 'https:' + news_url
                    else:
                        urls = 'https://hindi.cri.cn' + news_url
                else:
                    urls = news_url
                if news_url.find('.cri.cn') != -1:
                    news_url = news_url[news_url.find('.cri.cn') + 7:]
                if news_url[5] == '/' or news_url[5] == '-':
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[6:8] + '-' + news_url[9:11] + ' 00:00:00'
                else:
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[5:7] + '-' + news_url[7:9] + ' 00:00:00'
                if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield Request(url=urls, callback=self.parse_item, meta=response.meta)
            menu2 = soup.select('#contentELMT5GG6y2lk0S2KjrtPiLrb220418 > ul > li')
            for i in menu2:
                response.meta['category2'] = 'महादेश'
                # print(i)
                news_url = (i.select_one('a').get('href'))
                # print(news_url)
                response.meta['title'] =(i.select_one('a > div.subtitle').text)
                if news_url.find('http') == -1:
                    if news_url[1] == '/':
                        urls = 'https:' + news_url
                    else:
                        urls = 'https://hindi.cri.cn' + news_url
                else:
                    urls = news_url
                if news_url.find('.cri.cn') != -1:
                    news_url = news_url[news_url.find('.cri.cn') + 7:]
                if news_url[5] == '/' or news_url[5] == '-':
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[6:8] + '-' + news_url[9:11] + ' 00:00:00'
                else:
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[5:7] + '-' + news_url[7:9] + ' 00:00:00'
                if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield Request(url=urls, callback=self.parse_item, meta=response.meta)
            menu3 = soup.select('#contentELMTkMPcROqRz1sVaUA1jaNx220418 > ul > li')
            for i in menu3:
                response.meta['category2'] = 'अन्य'
                news_url = (i.select_one('a').get('href'))
                # print(news_url)
                response.meta['title'] = i.select_one('a > div.subtitle').text
                if news_url.find('http') == -1:
                    if news_url[1] == '/':
                        urls = 'https:' + news_url
                    else:
                        urls = 'https://hindi.cri.cn' + news_url
                else:
                    urls = news_url
                if news_url.find('.cri.cn') != -1:
                    news_url = news_url[news_url.find('.cri.cn') + 7:]
                if news_url[5] == '/' or news_url[5] == '-':
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[6:8] + '-' + news_url[9:11] + ' 00:00:00'
                else:
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[5:7] + '-' + news_url[7:9] + ' 00:00:00'
                if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield Request(url=urls, callback=self.parse_item, meta=response.meta)
        elif response.meta['category1'] == 'टिप्पणी':
            menu = soup.select('body > div.main.pagewrap > div.w1200 > div > div.container > div > div > div > div.ptbList.list-col01.pic-lr > ul > li')
            for i in menu:
                response.meta['category2'] = 'टिप्पणी'
                news_url = (i.select_one('div > div > h3 > a').get('href'))
                response.meta['title'] =(i.select_one('div > div.txtArea > h3 > a').text)
                if news_url.find('https') == -1:
                    if news_url[1] == '/':
                        urls = 'https:' + news_url
                    else:
                        urls = 'https://hindi.cri.cn' + news_url
                else:
                    urls = news_url
                if news_url.find('.cri.cn') != -1:
                    news_url = news_url[news_url.find('.cri.cn') + 7:]
                if news_url[5] == '/' or news_url[5] == '-':
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[6:8] + '-' + news_url[9:11] + ' 00:00:00'
                else:
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[5:7] + '-' + news_url[7:9] + ' 00:00:00'
                if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield Request(url=urls, callback=self.parse_item, meta=response.meta)
        elif response.meta['category1'] == 'तिब्बत':
            menu = soup.select('#contentELMTAAUpWVLx6eKqLYMmc7sd220419 > ul > li')
            for i in menu:
                response.meta['category2'] = 'तिब्बत'
                news_url = (i.select_one('a').get('href'))
                response.meta['title'] =(i.select_one('a > div.subtitle').text)
                if news_url.find('https') == -1:
                    if news_url[1] == '/':
                        urls = 'https:' + news_url
                    else:
                        urls = 'https://hindi.cri.cn' + news_url
                else:
                    urls = news_url
                if news_url.find('.cri.cn') != -1:
                    news_url = news_url[news_url.find('.cri.cn') + 7:]
                if news_url[5] == '/' or news_url[5] == '-':
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[6:8] + '-' + news_url[9:11] + ' 00:00:00'
                else:
                    last_time = response.meta['pub_time'] = news_url[1:5] + '-' + news_url[5:7] + '-' + news_url[7:9] + ' 00:00:00'
                if OldDateUtil.time is None or int(OldDateUtil.time) < OldDateUtil.str_datetime_to_timestamp(last_time):
                    yield Request(url=urls, callback=self.parse_item, meta=response.meta)
    def parse_item(self,response):
        soup=BeautifulSoup(response.text,'lxml')
        item = NewsItem(language_id=self.language_id)
        image=[]
        p_list=[]
        all_p = soup.select('#abody > p')
        item['abstract'] =''
        for i in all_p:
            try:
                img = i.select_one('img').get('src')
                if img.find('https://') == -1:
                    img = 'https:' + img
                image.append(img)
            except:
                pass
            p_list.append(i.text.strip())
        if response.meta['category1']=='वीडियो':
            all_image = soup.select('#abody > video')
            for i in all_image:
                try:
                    img = i.select_one('img').get('src')
                    if img.find('https://') == -1:
                        img = 'https:' + img
                    image.append(img)
                except:
                    pass
            for i in all_p:
                try:
                    img = i.select_one('span > video').get('src')
                    if img.find('https://') == -1:
                        img = 'https:' + img
                    image.append(img)
                except:
                    pass
                try:
                    img = i.select_one('audio').get('src')
                    if img.find('https://') == -1:
                        img = 'https:' + img
                    image.append(img)
                except:
                    pass
                p_list.append(i.text.strip())
        item['title'] = response.meta['title']
        item['category1'] = response.meta['category1']
        item['category2'] = response.meta['category2']
        item['body'] = '\n'.join(p_list)
        if len(p_list)>0:
            item['abstract'] = p_list[0]
        item['pub_time'] = response.meta['pub_time']
        item['images'] = image
        if len(item['abstract']) != 0 or len(item['body']) != 0 or len(item['images']) != 0:
            yield item