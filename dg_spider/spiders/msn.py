import json
from scrapy import Request
from dg_spider.items import NewsItem
import scrapy
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil



from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil as mutong

urls={
    '焦點新聞':'https://assets.msn.com/service/MSN/Feed?$top=30&DisableTypeSerialization=true&apikey=0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM&cipenabled=false&fdhead=msnallexpusers,muidflt13cf,'
    'muidflt15cf,muidflt21cf,muidflt27cf,muidflt51cf,muidflt301cf,startedge2cf,bingcollabedge1cf,starthp2cf,modcoglangc,platagyhz2cf,bingcollabhz3cf,'
    'prg-ads-t-onesz-r2,prg-ads-onesz,prg-da21rf2,prg-tok21,shophp2cf,sagehz1cf,weather4cf,prg-ntbell-expt,prg-commonbell,prg-nt-vertical,prg-1sw-prepwr,prg-1sw-sdb7,'
    'routeauthexp,prg-adspeek,infra-ceto-t,btrecrow3,1s-winauthservice,prg-1sw-sphnffc,wf-sunny-first,weather8cf,prg-1sw-clbdg,1s-p2-brknb,1s-p2cl-bdg,prg-1sbgbanner,prg-1sw-wxbdg,'
    'prg-1sw-clrot,prg-1s-mtsn,prg-1sw-wxrus,prg-ias,routentpring2t,1s-fcrypt,prg-wpo-layoutc,prg-wpo-b7arbq,prg-1sw-cgrndc,prg-wpo-pnpc,prg-pr2-crslrank,prg-1sw-p2localnews,prg-1sw-p2video,'
    'prg-1sw-p2webnews,prg-1sw-pr2tspos-s,prg-pr2-crsldft,prg-pr2-crsldfte,prg-prong2-crsl,prg-upsaip-w1-t,prg-upsaip-r-t,ads-msanapac,prg-wx-anmpr,prg-wtch-srchdel,prg-wea-allxap,prg-wea-subxap,'
    'a83d7349,prg-wx-sbn-vm,prg-1sw-sbn-mm,prg-1sw-pmosg,1s-rpssecautht,ads-dyndom,prg-apilogcon,prg-1sw-p1wtrclm,prg-1sw-mbnodp,prg-1sw-sbnww-c,prg-1sw-wxcfwf,prg-1sw-bg23,prg-1sw-stul2,prg-1sw-stmlc,prg-m-hurr,'
    'prg-1sw-sphstp,prg-1sw-sphdn,prg-nosearchbox,prg-1sw-msnhfl,prg-1sw-cwinphfl,prg-1sw-winphm,prg-1sw-wblis,prg-1sw-hcnwc,prg-1sw-chident,prg-1sw-wxcfetrc,prg-wea-tempv2,prg-highlightcc&ids=Y_b84a10de-febb-4502-9290-794653c27ed2&'
    'infopaneCount=5&location=22.2578|114.166&market=zh-hk&ocid=EMMX&queryType=myfeed&responseSchema=cardview&'
    'timeOut=1000&user=m-3AED6F02A59D6F632F377EF9A4446EE1&wrapodata=false',

    '兩岸國際':'https://assets.msn.com/service/MSN/Feed?$top=30&DisableTypeSerialization=true&apikey=0QfOX3Vn51YCzitbLaRkTTBadtWpgTN8NZLW0C1SEM&cipenabled=false&fdhead=msnallexpusers,'
           'muidflt13cf,muidflt15cf,muidflt21cf,muidflt27cf,muidflt51cf,muidflt301cf,startedge2cf,'
           'bingcollabedge1cf,starthp2cf,modcoglangc,platagyhz2cf,bingcollabhz3cf,prg-ads-t-onesz-r2,prg-ads-onesz,prg-da21rf2,'
           'prg-tok21,shophp2cf,sagehz1cf,weather4cf,prg-ntbell-expt,prg-commonbell,prg-nt-vertical,prg-1sw-prepwr,prg-1sw-sdb7,'
           'routeauthexp,prg-adspeek,infra-ceto-t,btrecrow3,1s-winauthservice,prg-1sw-sphnffc,wf-sunny-first,weather8cf,'
           'prg-1sw-clbdg,1s-p2-brknb,1s-p2cl-bdg,prg-1sbgbanner,prg-1sw-wxbdg,prg-1sw-clrot,prg-1s-mtsn,prg-1sw-wxrus,prg-ias,'
           'routentpring2t,1s-fcrypt,prg-wpo-layoutc,prg-wpo-b7arbq,prg-1sw-cgrndc,prg-wpo-pnpc,prg-1sw-stcboc,prg-pr2-crslrank,'
           'prg-1sw-p2localnews,prg-1sw-p2video,prg-1sw-p2webnews,prg-1sw-pr2tspos-s,prg-pr2-crsldft,prg-pr2-crsldfte,prg-prong2-crsl,'
           'prg-upsaip-w1-t,prg-upsaip-r-t,ads-msanapac,prg-wx-anmpr,prg-wtch-srchdel,a83d7349,prg-wx-sbn-vm,prg-1sw-sbn-mm,prg-1sw-pmosg,1s-rpssecautht,ads-dyndom,prg-apilogcon,'
           'prg-1sw-p1wtrclm,prg-1sw-mbnodp,prg-1sw-sbnww-c,prg-1sw-wxcfwf,prg-1sw-bg23,ads-tabbeaconhld,prg-1sw-stul2,prg-1sw-stmlc,prg-m-hurr,prg-1sw-sphstp,prg-1sw-sphdn,'
           'prg-nosearchbox,prg-1sw-msnhfl,prg-1sw-cwinphfl,prg-1sw-winphm,prg-1sw-wblis,prg-1sw-hcnwc,prg-1sw-chident,prg-1sw-weartc,prg-1sw-wxcfetrc,'
           '8i7cd893,prg-wea-tempv2,'
           'prg-highlightcc&ids=Y_5c3e9893-eca1-4913-8c5f-77b02f294511&infopaneCount=5&'
           'location=22.2578|114.166&market=zh-hk&ocid=EMMX&queryType=myfeed&responseSchema=cardview&'
           'timeOut=1000&user=m-3AED6F02A59D6F632F377EF9A4446EE1&wrapodata=false'
}

class msnSpider(BaseSpider):
    name = 'msn'
    website_id = 436
    language_id = 1866
    start_urls = ['https://www.msn.com/zh-hk/news/']

#aurhor：李沐潼
# check:wpf pass
    def parse(self, response):
        meta={}
        meta['category1']='新聞'
        for i in urls:
            meta['category2']=i
            yield Request(urls[i],meta=meta,callback=self.parse_page)


    def parse_page(self,response):
        try:
            js = json.loads(response.text)
            new_url=''
            for i in js['subCards']:
                try:
                    new_url_try= i['url']
                    new_url='https://assets.msn.com/content/view/v2/Detail/zh-hk/' + new_url_try.split('ar-')[1].split('?')[0]
                except:
                    for j in i['subCards']:
                        new_url_try = j['url']
                        new_url='https://assets.msn.com/content/view/v2/Detail/zh-hk/' + new_url_try.split('ar-')[1].split('?')[0]

                yield Request(new_url,meta=response.meta,callback=self.parse_items)

            next_url = js['nextPageUrl']
            yield Request(next_url, meta=response.meta, callback=self.parse_page)
        except:
            pass


    def parse_items(self,response):
        js = json.loads(response.text)
        pub_time_try = js['publishedDateTime']
        pub_time = '{} {}'.format(pub_time_try.split('T')[0],pub_time_try.split('T')[1].split('Z')[0])

        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1']=response.meta['category1']
            item['category2'] = response.meta['category2']
            item['pub_time']=pub_time
            # print(pub_time)
            title =js['title']
            item['title']=title

            body_str = js['body']
            body_li = mutong(body_str, 'html.parser')
            body = ''.join(i.text.strip() for i in body_li)
            item['body']=body

            item['abstract']=js['abstract']

            images = []
            for i in js['imageResources']:
                images.append(i['url'])
            item['images']=images


            yield item



