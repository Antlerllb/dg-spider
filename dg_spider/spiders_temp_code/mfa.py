

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
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldFormatUtil
from dg_spider.utils.old_utils import OldDateUtil

# author: 蔡卓妍

# check:why

month = {
    'Ocak': '01',
    'Şubat': '02',
    'Mart': '03',
    'Nisan': '04',
    'Mayıs': '05',
    'Haziran': '06',
    'Temmuz': '07',
    'Ağustos': '08',
    'Eylül': '09',
    'Ekim': '10',
    'Kasım': '11',
    'Aralık': '12'
} # 土耳其语月份

def p_time(title): #文章里没有具体时间，从title里获取
    time1 = title.split(",")
    try:
        time = time1[1].split()[2].strip()+"-"+month[time1[1].split()[1]]+"-"+time1[1].split()[0].split("-")[0].strip()+" 00:00:00"
    except:
        try:
            time = time1[-1].split()[2].strip()+"-"+month[time1[-1].split()[1]]+"-"+time1[-1].split()[0].split("-")[0].strip()+" 00:00:00"
        except: #有部分获取不到
            time = OldDateUtil.get_now_datetime_str()
    return OldDateUtil.str_datetime_to_timestamp(str(time))

class MfaSpider(BaseSpider):
    name = 'mfa'
    website_id = 2089
    language_id = 2227
    start_urls = ['https://www.mfa.gov.tr/sub.tr.mfa?978045a8-225a-487d-8fd8-8d371874e8ec',
                  'https://www.mfa.gov.tr/sub.tr.mfa?3fc6582e-a37b-40d1-847a-6914dc12fb60'] #最新报道+最新动态
    proxy = '02'

    def parse(self,response):
        soup = BeautifulSoup(response.text,'html.parser')
        flag = True
        last_time = p_time(soup.select(".sub_lstitm")[-1].text.strip())
        if OldDateUtil.time is None or int(last_time) >= int(OldDateUtil.time):
            lists = soup.select(".sub_lstitm")
            for i in lists:
                article = "https://www.mfa.gov.tr" + i.select_one('a').get("href")
                pub_time = OldDateUtil.timestamp_to_datetime_str(p_time(i.text.strip()))
                meta = {'pub_time': pub_time}
                yield Request(url=article, callback=self.parse_item, meta=meta)
        else:
            flag = False
            self.logger.info("时间截止")
        if flag: # 翻页(第一页请求为get 后面为post
            num = int(soup.select_one('#sb_grd tr > td span').text) + 1
            form_data ={ '__EVENTTARGET': 'sb$grd',
                         '__EVENTARGUMENT': f'Page${num}',
                         '__VIEWSTATEGENERATOR':'9B4A3EDA',
                         '__VIEWSTATE': soup.find(id="__VIEWSTATE").get('value'),
                         '__EVENTVALIDATION': soup.find(id="__EVENTVALIDATION").get('value')}
            yield scrapy.FormRequest(url=response.url, formdata=form_data, callback=self.parse, meta=response.meta)

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = soup.select(".breadcrumb a")[2].text
        item['category1'] = soup.select(".breadcrumb a")[0].text
        item['category2'] = soup.select(".breadcrumb a")[1].text
        item['body'] = "".join(i.text.replace("\n","\r").lstrip().replace("\r\r","\n") for i in (soup.find_all(align='justify')))
        item['abstract'] = soup.find(align='justify').text.strip() if soup.find(align='justify').text.strip() != "" else soup.find_all(align='justify')[1].text.strip()
        item['images'] = ["https://www.mfa.gov.tr" + i.get("href") for i in soup.select(".mfagallerylink")] #大部分没有图片
        item['pub_time'] = response.meta['pub_time']
        yield item