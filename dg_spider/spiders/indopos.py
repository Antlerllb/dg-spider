# -- coding: utf-8 --**



from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
import json
import copy
import scrapy
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil
from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

Month = {'Januari': '01',
         'Februari': '02',
         'Maret': '03',
         'April': "04",
         'Mei': '05',
        'Juni': '06',
        'Juli': '07',
        'Agustus': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Desember': '12'} # 印尼语月份

#author:蔡卓妍
def p_time(pt):
    ptime = pt.split(',')[1].strip().split()
    if len(ptime[0]) < 2:
        ptime[0] = '0' + ptime[0]
    l_time = ptime[2] + '-' + Month[ptime[1]] + '-' + ptime[0] + ' ' + ptime[4] + ':00'
    return l_time

class IndoposSpider(BaseSpider):
    name = 'indopos'
    website_id = 46
    language_id = 1952
    start_urls = ['https://www.indopos.co.id/nasional/',
                  'https://www.indopos.co.id/megapolitan/',
                  'https://www.indopos.co.id/nusantara/',
                  'https://www.indopos.co.id/internasional/',
                  'https://www.indopos.co.id/gayahidup/',
                  'https://www.indopos.co.id/ekonomi/',
                  'https://www.indopos.co.id/olahraga/',
                  'https://www.indopos.co.id/koran-indopos/']
    post_url = 'https://www.indopos.co.id/?ajax-request=jnews'
    data = {'lang': 'id_ID',
            'action': 'jnews_module_ajax_jnews_block_3',
            'module': 'true',
            'data[current_page]': '1'}
    page = {'page1':'1', 'page2':'1', 'page3':'1', 'page4':'1',
            'page5':'1', 'page6':'1', 'page7':'1', 'page8':'1'}
    proxy = '02'

    def parse(self, response): #除了URL以外 其余从具体新闻中获取
        try:
            if response.url == self.post_url:
                soup1 = json.loads(response.text)
                soup = BeautifulSoup(soup1["content"], "html.parser")
                category1 = copy.deepcopy(response.meta['category1'])
            else:
                soup = BeautifulSoup(response.text,'html.parser')
                category1 = copy.deepcopy(response.url.split('/')[3].strip())
            flag = True
            l_time = soup.select(".jeg_meta_date")[9].text.strip()
            last_time = p_time(l_time)
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
                lists = soup.select('.jeg_postblock_content')[:10] #只有10条是该类的新闻 其余是单日热点（内容重复
                for i in lists:
                    news_url = i.select_one('a')['href']
                    yield Request(url=news_url, callback=self.parse_item, meta={'category1':category1},dont_filter=True)
            else:
                flag = False
                self.logger.info("时间截止")
            if flag:  # 翻页post
                if category1 == 'nasional':
                    self.data['data[attribute][include_category]']='74'
                    self.page['page1'] = str(int(self.page['page1']) + 1)
                    self.data['data[current_page]'] = str(self.page['page1'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'megapolitan':
                    self.data['data[attribute][include_category]']='75'
                    self.page['page2'] = str(int(self.page['page2']) + 1)
                    self.data['data[current_page]'] = str(self.page['page2'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'nusantara':
                    self.data['data[attribute][include_category]']='76'
                    self.page['page3'] = str(int(self.page['page3']) + 1)
                    self.data['data[current_page]'] = str(self.page['page3'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'internasional':
                    self.data['data[attribute][include_category]']='77'
                    self.page['page4'] = str(int(self.page['page4']) + 1)
                    self.data['data[current_page]'] = str(self.page['page4'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'gayahidup':
                    self.data['data[attribute][include_category]']='78'
                    self.page['page5'] = str(int(self.page['page5']) + 1)
                    self.data['data[current_page]'] = str(self.page['page5'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'ekonomi':
                    self.data['data[attribute][include_category]']='79'
                    self.page['page6'] = str(int(self.page['page6']) + 1)
                    self.data['data[current_page]'] = str(self.page['page6'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'olahraga':
                    self.data['data[attribute][include_category]']='80'
                    self.page['page7'] = str(int(self.page['page7']) + 1)
                    self.data['data[current_page]'] = str(self.page['page7'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'koran-indopos':
                    self.data['data[attribute][include_category]']='2899'
                    self.page['page8'] = str(int(self.page['page8']) + 1)
                    self.data['data[current_page]'] = str(self.page['page8'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1':category1},dont_filter=True)
        except:
            self.logger.info("no more pages")

    def parse_item(self,response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text,'html.parser')
        item['title'] = soup.select_one('.jeg_post_title').text
        item['category1'] = response.meta['category1']
        try:
            item['body'] = "\n".join(i.text.strip() for i in soup.select('.content-inner p'))
            item['abstract'] = soup.select_one('.content-inner p').text.strip()
        except:
            item['body'] = '\n'.join(i.text.strip() for i in soup.find_all(dir='auto'))
            item['abstract'] = soup.find(dir='auto').text.strip()
        ptime = soup.select_one(".jeg_meta_date").text.strip()
        item['pub_time'] = p_time(ptime)
        item['images'] = [soup.select_one('.thumbnail-container img').get('src')]
        return item