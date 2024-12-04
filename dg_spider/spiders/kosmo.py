#
# encoding: utf-8
import copy
import json

from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



from scrapy.http.request import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil


import re
import scrapy
import requests

time_dict = {'Januari': '01', 'Februari': '02', 'Mac': '03', 'April': '04', 'Mei': '05', 'Jun': '06', 'Julai': '07',
             'Ogos': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Disember': '12', 'pm': 12, 'am': 0}

def p_time(pt):

    time_list = re.split(r'[,:\'\s]\s*', pt)  # %Y-%m-%d %H:%M:%S
    if int(time_list[3]) == 12:
        hh = int(time_list[3])
    else:
        hh = str(int(time_list[3]) + time_dict[time_list[-1]])
    time_ = "{}-{}-{} {}:{}:{}".format(time_list[2], time_dict[time_list[1]], time_list[0], hh,
                                           time_list[-2], "00")
    return time_
# author: 华上瑛

class KosmoSpider(BaseSpider):
    name = 'kosmo'
    website_id = 174
    language_id = 2036
    start_urls = ['https://www.kosmo.com.my/negara/','https://www.kosmo.com.my/k2/','https://www.kosmo.com.my/hib-glam/',
                  'https://www.kosmo.com.my/dunia/','https://www.kosmo.com.my/sukan/',
                  'https://www.kosmo.com.my/ahad/','https://www.kosmo.com.my/video/','https://www.kosmo.com.my/premium/','https://www.kosmo.com.my/terkini/'] # 'https://www.kosmo.com.my/terkini/',
    # start_urls = ['https://www.kosmo.com.my/k2/']
    post_url = 'https://www.kosmo.com.my/?epic-ajax-request=epic-ne'
    data = {
            'action': 'epic_module_ajax_epic_block_19',
            'module': 'true',
            'data[current_page]': '1',
            'data[attribute][header_filter_text]': 'SEMUA',
            'data[attribute][number_post][size]':'6',
            'data[attribute][post_offset]':'0',
            'data[attribute][pagination_number_post][size]': '10',
            'data[attribute][header_type]': 'heading_1'
    }
    page = {'page1': '1', 'page2': '1', 'page3': '1', 'page4': '1',
            'page5': '1', 'page6': '1', 'page7': '1', 'page8': '1','page9': '1','page10': '1'}
    proxy = '02'
    # headers = {
    #     'accept': 'application/json, text/javascript, */*; q=0.01',
    #     'accept-encoding': 'gzip, deflate, br',
    #     'accept-language': 'zh-CN,zh;q=0.9',
    #     'content-length':'31841',
    #     'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
    #     'cookie':'tk_or=%22%22; tk_lr=%22%22; cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; __stdf=0; _cc_id=4c2bc123d7ca70d37c5cb315222f716d; panoramaId=7f321c7f3785868a8366cf55742b4945a702c140bf7f159baf73d36be7b3a18d; _fbp=fb.2.1657198353399.713729794; _cb=DG2WreBquyDPDeRs65; dable_uid=38885132.1657198204296; __stp={"visit":"returning","uuid":"019210fc-d69e-42d2-9427-316836ab9f79"}; __stat="BLOCK"; _ga=GA1.3.395041496.1657541809; __utmc=119768722; __utmz=119768722.1657541982.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __gads=ID=4af6822106409463:T=1657541983:S=ALNI_MZk4vp0mxyCT3OnkVz1opTwvmcUOQ; __gpi=UID=0000079730bf9c94:T=1657541983:RT=1657592960:S=ALNI_MYpzbEoIRny8WpFLVDVC2sqzyYhiw; __utma=119768722.395041496.1657541809.1657592960.1657605446.3; iUUID=6654b486953f1840fac2f4e51eab307d; X_CACHE_KEY=43c204901d92c04049c6b8d41f517290; tk_r3d=%22%22; __stgeo="0"; __stbpnenable=1; _cb_svref=null; __sts={"sid":1658035898840,"tx":1658035930257,"url":"https%3A%2F%2Fwww.kosmo.com.my%2Fterkini%2F","pet":1658035930257,"set":1658035898840,"pUrl":"https%3A%2F%2Fwww.kosmo.com.my%2Fterkini%2Fpage%2F43%2F","pPet":1658035922589,"pTx":1658035922589}; _chartbeat2=.1657198353589.1658037426051.10001111001.DIaWb3aN97wDayB3PCsZWqwD2dwhd.5; panoramaId_expiry=1658642225658; advanced_ads_browser_width=358; _chartbeat5=117|3217|%2Fterkini%2F|https%3A%2F%2Fwww.kosmo.com.my%2Fterkini%2F|Ub_fqCTpZYB9tgxTmQ6ImCoVPSV||c|cK26lDvnRcaDIFuVGDI0EvMCeq7_p|kosmo.com.my|',
    #     'origin':'https://www.kosmo.com.my',
    #     'referer':'https://www.kosmo.com.my/terkini/',
    #     'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    #     'sec-ch-ua-mobile': '?1',
    #     'sec-ch-ua-platform': '"Android"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'same-origin',
    #     'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36',
    #     'x-requested-with':'XMLHttpRequest'
    # }
    custom_settings = {'DOWNLOAD_TIMEOUT': 100, 'DOWNLOADER_CLIENT_TLS_METHOD' :"TLSv1.2",'RETRY_TIMES':10,'DOWNLOAD_DELAY':0.1,'RANDOMIZE_DOWNLOAD_DELAY':True}

    def start_requests(self):
        for i in self.start_urls:
            yield Request(url=i,callback=self.parse)

    def parse(self, response):
        try:
            if response.url == self.post_url:
                soup1 = json.loads(response.text)
                soup = BeautifulSoup(soup1["content"], "html.parser")
                category1 = copy.deepcopy(response.meta['category1'])
                articles = soup.select('article')
            else:
                soup = BeautifulSoup(response.text,'html.parser')
                category1 = copy.deepcopy(response.url.split('/')[-2].strip())
                if category1 == 'terkini':
                    articles = soup.select('div.elementor-element.elementor-element-1564c4f.custom-post.elementor-hidden-tablet.elementor-hidden-mobile.elementor-widget.elementor-widget-epic_block_22_elementor > div > div > div > div > div > article')
                elif category1 == 'video':
                    articles = soup.select('div.elementor-element.elementor-element-1a55f04.page-design.elementor-widget.elementor-widget-epic_block_19_elementor > div > div > div > div > div > article')
                else:
                    articles = soup.select('div.jeg_postsmall.jeg_load_more_flag > article')

            flag = True
            l_time = articles[-1].select('div > div > div > a')[0].text.strip()
            last_time = p_time(l_time)
            if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(str(last_time)) >= int(OldDateUtil.time):
                # lists = soup.select('.jeg_postblock_content')[:10] #只有10条是该类的新闻 其余是单日热点（内容重复
                for article in articles:
                    # news_url = i.select_one('a')['href']
                    news_url = article.select('div > a')[0].get('href')
                    time = article.select('div > div > div > a')[0].text.strip()
                    pub_time = p_time(time)
                    yield Request(url=news_url, callback= self.parse_item, meta={'category1':category1,'pub_time':pub_time},dont_filter=True)
            else:
                flag = False
                self.logger.info("时间截止")

            if flag:  # 翻页post
                if category1 == 'terkini':
                    self.data['data[attribute][include_category]'] = '15'
                    self.data['action']= 'epic_module_ajax_epic_block_22'
                    self.data['data[attribute][header_filter_text]']= 'All'
                    self.data['data[attribute][number_post][size]']= '2'
                    self.data['data[attribute][post_offset]']= '7'
                    self.data['data[attribute][pagination_number_post][size]']= '8'
                    # self.data['data[attribute][first_title]'] = response.url.split('/')[-2]
                    self.page['page1'] = str(int(self.page['page1']) + 1)
                    self.data['data[current_page]'] = str(self.page['page1'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'negara':
                    self.data['data[attribute][include_category]'] = '75'
                    self.page['page2'] = str(int(self.page['page2']) + 1)
                    self.data['data[current_page]'] = str(self.page['page2'])

                    self.data['data[attribute][first_title]'] = 'NEGARA'
                    self.data['data[attribute][header_filter_category]']= '76, 77, 78, 113, 80'
                    # self.data['data[attribute][header_filter_text]'] = 'SEMUA'
                    # self.data['data[attribute][number_post][size]'] = '6'
                    # self.data['data[attribute][post_offset]'] = '0'
                    # self.data['data[attribute][pagination_number_post][size]'] = '10'
                    # self.data['data[attribute][header_type]'] = 'heading_1'

                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'k2':
                    self.data['data[attribute][include_category]'] = '82,83,84,85,86,129'
                    self.page['page3'] = str(int(self.page['page3']) + 1)
                    self.data['data[current_page]'] = str(self.page['page3'])

                    self.data['data[attribute][first_title]'] = 'K2'
                    self.data['data[attribute][header_filter_category]'] = '82,83,84,85,86,129'

                    # self.data['data[attribute][header_filter_text]'] = 'SEMUA'
                    # self.data['data[attribute][number_post][size]'] = '6'
                    # self.data['data[attribute][post_offset]'] = '0'
                    # self.data['data[attribute][pagination_number_post][size]'] = '10'
                    # self.data['data[attribute][header_type]'] = 'heading_1'

                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'hib-glam':
                    self.data['data[attribute][include_category]'] = '87'
                    self.page['page4'] = str(int(self.page['page4']) + 1)
                    self.data['data[current_page]'] = str(self.page['page4'])

                    self.data['data[attribute][first_title]'] = 'HIB GLAM'
                    self.data['data[attribute][header_filter_category]'] = '88,89,130,91,92,170,131,94,169'

                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'dunia':
                    self.data['data[attribute][include_category]'] = '124'
                    self.data['data[attribute][first_title]'] = 'DUNIA'
                    self.page['page5'] = str(int(self.page['page5']) + 1)
                    self.data['data[current_page]'] = str(self.page['page5'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'sukan':
                    self.data['data[attribute][include_category]'] = '14'
                    self.data['data[attribute][first_title]'] = 'SUKAN'
                    self.page['page6'] = str(int(self.page['page6']) + 1)
                    self.data['data[current_page]'] = str(self.page['page6'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'niaga':
                    self.data['data[attribute][include_category]'] = '109'

                    self.data['data[attribute][first_title]'] = 'NIAGA'

                    self.page['page7'] = str(int(self.page['page7']) + 1)
                    self.data['data[current_page]'] = str(self.page['page7'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'ahad':
                    self.data['data[attribute][include_category]'] = '98'
                    self.page['page8'] = str(int(self.page['page8']) + 1)
                    self.data['data[current_page]'] = str(self.page['page8'])

                    self.data['data[attribute][first_title]'] = 'AHAD'
                    self.data['data[attribute][header_filter_category]'] = '99,105'

                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'video':

                    self.data['data[attribute][include_category]'] = '16'
                    self.data['data[attribute][first_title]'] = 'VIDEO'

                    self.page['page9'] = str(int(self.page['page9']) + 1)
                    self.data['data[current_page]'] = str(self.page['page9'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
                elif category1 == 'premium':
                    self.data['data[attribute][include_category]'] = '12'
                    self.data['data[attribute][first_title]'] = 'PREMIUM'
                    self.page['page10'] = str(int(self.page['page10']) + 1)
                    self.data['data[current_page]'] = str(self.page['page10'])
                    yield scrapy.FormRequest(url=self.post_url, formdata=self.data, callback=self.parse,
                                             meta={'category1': category1}, dont_filter=True)
        except:
            self.logger.info("no more pages")

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        item = NewsItem(language_id=self.language_id)
        # content = soup.select('div.entry-content')[0]
        content = soup.select('div.dable-content-wrapper > p')

        try:
            img = [soup.select('figure.wp-caption > img')[0].get('src')]
        except:
            img = []

        if len(content)==0:
            content = soup.select('div.elementor-element.elementor-element-3de77384.elementor-widget.elementor-widget-theme-post-content > div > p')

        body = " "
        for b in content:
            body += b.text



        abstract = body.split('.')[0]
        title = soup.select('h1.elementor-heading-title.elementor-size-default')[0].text
        item['category1'] = response.meta['category1']
        item['category2'] = ""
        item['title'] = title
        item['pub_time'] = response.meta['pub_time']
        item['images'] = img
        item['body'] = body
        item['abstract'] = abstract
        item['title'] = title
        yield item


