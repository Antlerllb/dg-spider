
from scrapy import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil



import scrapy
import requests
from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil as mutong
import json


e_month_sim={
        'Jan':'01',
        'Feb':'02',
        'Mar':'03',
        'Apr':'04',
        'May':'05',
        'Jun':'06',
        'Jul':'07',
        'Aug':'08',
        'Sept':'09',
        'Sep':'09',
        'Oct':'10',
        'Nov':'11',
        'Dec':'12'
}
headers = {
         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
 }
cookies={
'__gads':'ID=8bbb073f121c90bf:T=1659195368:RT=1659255561:S=ALNI_MbCYimRA0AhUWkcRquGT04Hlbq7pQ',
'__gpi':'UID=000008222fd56ec3:T=1659195368:RT=1659238792:S=ALNI_MZnm2Pq_sXRo2Y5-8KqeEmTr1jmjw',
'_cb':'BLJnyZmI4Du0qoU1',
'_cb_svref':'https%3A%2F%2Fwww.beritaharian.sg%2Fgah',
'_chartbeat2':'.1659195372220.1659255562005.11.DtaA3PCaBKJYBbA9qUCAT_8HDkGzRx.1',
'_ga':'GA1.2.1226118676.1659195368',
'_gaexp':'GAX1.2.-Q2JoFkZTN-XeeYz8kADKw.19292.1',
'_gat':'1',
'_gat_UA-46304640-1':'1',
'_gcl_au':'1.1.2134195353.1659195368',
'_gid':'GA1.2.1530660674.1659195368',
'AWSALB':'gzmCqfMfut8y7+MxQEy79C+Na7hVE2s7GIXHqU/hob1Q3JEbmmFzYyuSnwJigFcjqor8HvQy+0n3LJdQtzBGaFFQVeCo1BneQ5ZV9VjN99lgExgq4betCc0ZfzTC',
'AWSALBCORS':'gzmCqfMfut8y7+MxQEy79C+Na7hVE2s7GIXHqU/hob1Q3JEbmmFzYyuSnwJigFcjqor8HvQy+0n3LJdQtzBGaFFQVeCo1BneQ5ZV9VjN99lgExgq4betCc0ZfzTC',
'mySPHUserType':'y-anoy',
'outbrain_cid_fetch':'true',
'outbrain_enable':'1',
'permutive-id':'8c80c58a-e5d4-4b45-a239-d00f0b761299',
'reload':'1',
'sessionStatus':'1',
'spgwAMCookie':'12178b2da47cb8b9ac4e47d82964637f',
'sph_seg':'S100011,S100087,S100089',
'sui_1pc':'16591953734755B7E0467804802C3BC8D6D6E5FF67A130F7243E8A1D',
'suid':'0f9ab04e38ed437e8c4313e40bc596be',
'topoverlayDisplayed':'yes',
'topOverlayImpressionsServed':'0',
'UserFirstVisit':'1',
'visitorcat':'1'
}

class beritaharianSpider(BaseSpider):
    i=0
    j=1
    name = 'beritaharian'
    website_id = 211
    language_id = 2036
    start_urls = ['https://www.beritaharian.sg/']


    # aurhor：李沐潼
    # check: wpf pass

    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}
        category1_li=soup.select('.clearfix>li')

        for i in category1_li:#各个类之间有交叉重合，所以可能出现一个新闻有两个归属的类，爬不同的类新闻有重合（重合不少）
            j=0
            meta['category1'] = i.text.strip()
            category1_url = 'https://www.beritaharian.sg/views/ajax?_wrapper_format=drupal_ajax'
            if i.text.strip()=='Akses Percuma':
                while True:
                    Akses = {
                        'view_name': 'web_category',
                        'view_display_id': 'page_1',
                        'view_path': '/akses-percuma',
                        'view_base_path': 'akses-percuma',
                        'view_dom_id': 'a83b8050de2342b523542e572fadfc4f32120207eb2ca2ae4d7a382f45fe3d70',
                        'pager_element': '0',
                        '_wrapper_format': 'drupal_ajax',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                        response1 = requests.post(category1_url, data=Akses, headers=headers, cookies=cookies)
                        js = json.loads(response1.text)
                        soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                        response1 = requests.post(category1_url, data=Akses, headers=headers)
                        js = json.loads(response1.text)
                        soup1 = mutong(js[2]['data'], 'html.parser')

                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                              callback=self.parse_items)
                    else:
                        break
            elif i.text.strip() =='Premium':
                while True:

                    Premium = {
                        'view_name': 'web_category',
                        'view_display_id': 'premium',
                        'view_path': '/premium-articles',
                        'view_base_path': 'premium-articles',
                        'view_dom_id': '2e5391f845956ddf5b15866a36accac40813e05649b7da09446ef554e3daa471',
                        'pager_element': '0',
                        '_wrapper_format': 'html',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Premium, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Premium, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break
            elif i.text.strip() =='Setempat':
                while True:

                    Setempat = {
                        'view_name': 'web_category',
                        'view_display_id': 'section_page',
                        'view_args': '27',
                        'view_path': '/taxonomy/term/27',
                        'view_base_path': 'taxonomy/term/%',
                        'view_dom_id': '6ede68cf96f2aaf5165796fccea166a86b3757a85085702b0c11f23babb1ddb6',
                        'pager_element': '0',
                        '_wrapper_format': 'drupal_ajax',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Setempat, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Setempat, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break
            elif i.text.strip() =='Dunia':
                while True:

                    Dunia = {
                        'view_name': 'web_category',
                        'view_display_id': 'section_page',
                        'view_args': '28',
                        'view_path': '/taxonomy/term/28',
                        'view_base_path': 'taxonomy/term/%',
                        'view_dom_id': 'fa80a2e6834f539d255354eac0f038707120919218bfd6e0e3ccd43131af87c5',
                        'pager_element': '0',
                        '_wrapper_format': 'html',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Dunia, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Dunia, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break
            elif i.text.strip() =='Ekonomi & Kerja':
                while True:

                    Ekonomi = {
                        'view_name': 'web_category',
                        'view_display_id': 'section_page',
                        'view_args': '29',
                        'view_path': '/taxonomy/term/29',
                        'view_base_path': 'taxonomy/term/%',
                        'view_dom_id': 'a45e7a294f1027da8a26c7733d6eb994b7b97f278b079e3ed3536b83ea4bf28b',
                        'pager_element': '0',
                        '_wrapper_format': 'drupal_ajax',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Ekonomi, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Ekonomi, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break
            elif i.text.strip()=='Sukan':
                while True:

                    Sukan = {
                'view_name': 'web_category',
                'view_display_id': 'section_page',
                'view_args': '30',
                'view_path': '/taxonomy/term/30',
                'view_base_path': 'taxonomy/term/%',
                'view_dom_id': '51ce13505bc344f2c296aa805951306556d79f31acc2a578bb2039cc56f86dff',
                'pager_element': '0',
                '_wrapper_format': 'html',
                'page': f'{j}',
                '_drupal_ajax': '1',
                'ajax_page_state[theme]': 'bh2021',
                'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                              'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                              'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                              'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                              'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                              'views/views.ajax,views/views.module,views_show_more/views_show_more'
                                }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Sukan, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Sukan, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break
            elif i.text.strip()=='Gaya Hidup':
                while True:

                    Gaya = {
                        'view_name': 'web_category',
                        'view_display_id': 'section_page',
                        'view_args': '31',
                        'view_path': '/taxonomy/term/31',
                        'view_base_path': 'taxonomy/term/%',
                        'view_dom_id': 'bd4f4bf2d5d2f274e15e22dbca16aa23fc7866d8dc456124f0e69e941533b7f1',
                        'pager_element': '0',
                        '_wrapper_format': 'html',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Gaya, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Gaya, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break
            elif i.text.strip()=='Hidayah':
                while True:

                    Hidayah = {
                        'view_name': 'web_category',
                        'view_display_id': 'section_page',
                        'view_args': '32',
                        'view_path': '/taxonomy/term/32',
                        'view_base_path': 'taxonomy/term/%',
                        'view_dom_id': '5360bbba4ea9c7b48fb558e65e1b84976b44d4214deb1b1a5def8531d004320e',
                        'pager_element': '0',
                        '_wrapper_format': 'drupal_ajax',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Hidayah, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Hidayah, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break
            elif i.text.strip() =='Rencana':
                while True:

                    Rencana = {
                        'view_name': 'web_category',
                        'view_display_id': 'section_page',
                        'view_args': '33',
                        'view_path': '/taxonomy/term/33',
                        'view_base_path': 'taxonomy/term/%',
                        'view_dom_id': 'fed445a3854135f598890389beeb07cf8116e9b7673eb68e4e2d23fa3c8a1a9f',
                        'pager_element': '0',
                        '_wrapper_format': 'html',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Rencana, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Rencana, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break
            elif i.text.strip() =='Wacana':
                while True:

                    Wacana = {
                        'view_name': 'web_category',
                        'view_display_id': 'section_page',
                        'view_args': '37',
                        'view_path': '/taxonomy/term/37',
                        'view_base_path': 'taxonomy/term/%',
                        'view_dom_id': '85b8699b47da9b06297e51da271ae733091e91129282d89a2c88c899954c0c92',
                        'pager_element': '0',
                        '_wrapper_format': 'html',
                        'page': f'{j}',
                        '_drupal_ajax': '1',
                        'ajax_page_state[theme]': 'bh2021',
                        'ajax_page_state[libraries]': 'bh2021/global-styling,bh_ga_tagging/tagging,'
                                                      'bootstrap_barrio/global-styling,bootstrap_barrio/messages_light,'
                                                      'layout_discovery/onecol,paragraphs/drupal.paragraphs.unpublished,'
                                                      'sph_dfp_betterads/sph-dfp-betterads,sph_firebase/sph-firebase,'
                                                      'sph_subscriber_login/sph-mysph,sph_translations/translations,system/base,'
                                                      'views/views.ajax,views/views.module,views_show_more/views_show_more'
                    }
                    if j > 0:
                                response1 = requests.post(category1_url, data=Wacana, headers=headers, cookies=cookies)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[1]['data'], 'html.parser')
                    else:
                                response1 = requests.post(category1_url, data=Wacana, headers=headers)
                                js = json.loads(response1.text)
                                soup1 = mutong(js[2]['data'], 'html.parser')
                    news_url = soup1.select('a')
                    j = j + 1
                    if news_url != []:
                        for i in news_url:
                            if i.select('img') != []:
                                yield Request('https://www.beritaharian.sg' + i.get('href'), meta=meta,
                                          callback=self.parse_items)
                    else:
                        break




    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')
        ti = soup.select('.date')[0].text.strip()
        ti_li = ti.split(' ')
        pub_time = "{}-{}-{} 00:00:00".format(ti_li[2], e_month_sim[ti_li[0]], ti_li[1][:-1])

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)


            item['title'] =soup.select('.article-headline')[0].text.strip()

            body_li = soup.select('p')
            body = ''.join([i.text for i in body_li[:-3]])
            item['body'] = body
            abstract = body_li[0].text
            item['abstract'] = abstract

            item['category1'] = response.meta['category1']
            item['category2'] = None

            item['pub_time'] = pub_time

            image_li = soup.select('.field__item>img')
            images = []
            if image_li != []:
                for image in image_li:
                    images.append(image.get('src'))
            else:
                pass
            item['images'] = images

            yield item
        else:
            return
