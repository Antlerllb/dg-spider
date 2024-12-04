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

import json,requests,datetime,re

# author:robot-2233
CA_dict = {
    '26': 'around',
    '3': 'local',
    '32': 'business',
    '5': 'entertainment',
    '37': 'qol',
    '43': 'game',
    '25': 'sport',
    '24': 'travel',
    '63': 'indochina',
    '18': 'politics',
    '49': 'stockmarket',
    '10': 'cyberbiz',
    '33': 'china',
    '1': 'uptodate',
    '45': 'science',
    '40': 'crime',
    '4': 'onlinesection',
    '11': 'pjkkuan',
    '14': 'greeninnovation',
    '42': 'motoring',
    '48': 'smes',
    '72': 'mutualfund',
    '79': 'celebonline',
    '83': 'japan',
    '2': 'south',
    '80': 'factcheck',
    '9': 'cbizreview',
    '17': 'infographic',
    '8': 'drama',
    '16': 'live',
    '12': 'goodhealth',
}  # 86 6 87

class managerSpider(BaseSpider):
    name = 'manager'  # 这是个聪明的网站，买了个小域名来分担主网站的压力，新闻资料均从这个小网站发出
    website_id = 239  # 它的规律就是基于加密的时间戳来返回新闻，所以可能会出现一个时间段内没有新闻的情况
    language_id = 2208  # 因为是基于时间的，所以使用了datetime来获得现在的时间，来获得最新的新闻
    start_urls = ['https://d1kolplw0yt85v.cloudfront.net/o.php']
    proxy = '02'
    RUN_TIME = '0000-00-00 00:00:00'  # 初始化起始时间

    def start_requests(self):
        now = datetime.datetime.now()
        DAY_now = f'{now.strftime("%Y-%m-%d")} {str(now.hour) if now.hour>=10 else ("0"+str(now.hour))}:00:00'
        managerSpider.RUN_TIME = DAY_now  # 它这个网站每一个小时回滚一次，更新新闻库
        yield Request(managerSpider.start_urls[0]+f'?d={now.strftime("%Y-%m-%d")}&m={DAY_now.split(" ")[1].split(":")[0]}%3A5', callback=self.parse)

    def parse(self, response):
        aim_json = requests.get(response.url)
        flag = True  # 暂时废弃的一个条件，本来以为返回的格式不一致需要多个条件，后来废弃了，不影响使用
        aim_news = json.loads(aim_json.text)['news']
        if aim_news:
            for detail in aim_news:
                time_ = detail['dateTime'].replace('/', '-')
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    managerSpider.RUN_TIME = time_
                    meta = {'pub_time_': time_, 'category2_': detail['tag'], 'title_': detail['topic'], 'abstract_': detail['intro']}
                    if 'image' in detail:
                        meta['images_'] = [detail['image']['image_url']]
                    else:
                        meta['images_'] = []
                    if detail["category"] in CA_dict:
                        url = f'https://mgronline.com/{CA_dict[detail["category"]]}/detail/{detail["id_"]}'
                        yield Request(url, callback=self.parse_item, meta=meta)
                    else:
                        self.log(f'Unexpected Error: Unknown category:{detail["category"]} with id_:{detail["id_"]}')
        else:
            if flag:
                managerSpider.RUN_TIME = json.loads(aim_json.text)['index']['older']+':00'
            else:
                Eyear = int(managerSpider.RUN_TIME.split('-')[0])
                Emonth = int(managerSpider.RUN_TIME.split('-')[1])
                Eday = int(managerSpider.RUN_TIME.split('-')[2].split(' ')[0])
                Ehour = int(managerSpider.RUN_TIME.split(' ')[1].split(':')[0])
                managerSpider.RUN_TIME = str(datetime.datetime(Eyear, Emonth, Eday, Ehour) + datetime.timedelta(hours=-1))
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(managerSpider.RUN_TIME) >= int(OldDateUtil.time):  # 本网站翻页机制（比较复杂，不建议初学者学习）
            if response.url[-1] != '0':
                yield Request(response.url[0:-1]+str(int(response.url[-1])-1))
            else:
                hour_now = int(response.url.split('&m=')[1].split('%')[0])
                if hour_now != 0:
                    if hour_now > 10:
                        yield Request(response.url[0:-6] + str(hour_now - 1) + '%3A5')
                    else:
                        yield Request(response.url[0:-6] + '0' + str(hour_now - 1) + '%3A5')
                else:
                    year = int(managerSpider.RUN_TIME.split('-')[0])
                    month = int(managerSpider.RUN_TIME.split('-')[1])
                    day = int(managerSpider.RUN_TIME.split('-')[2].split(' ')[0])
                    yes_time = datetime.datetime(year, month, day) + datetime.timedelta(days=-1)
                    yield Request(f'https://d1kolplw0yt85v.cloudfront.net/o.php?d={str(yes_time).split(" ")[0]}&m=23%3A5')

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        item = NewsItem(language_id=self.language_id)
        item['title'] = response.meta['title_']
        item['category1'] = response.url.split('.com/')[1].split('/detail')[0]
        item['category2'] = response.meta['category2_']
        item['body'] = soup.select_one(' .article-content .m-detail-container').text.strip().strip('\n')
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['pub_time_']
        item['images'] = response.meta['images_']
        yield item
