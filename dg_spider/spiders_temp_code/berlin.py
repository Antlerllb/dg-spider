# encoding: utf-8



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

# author: robot_2233
# check:wpf pass


class BerlinSpider(BaseSpider):
    name = 'berlin'  # 会出418报错，然后会重新爬，不影响
    website_id = 1705
    language_id = 1898
    start_urls = ['https://www.berlin.de/presse/pressemitteilungen/index/search/page/1?institutions%5B%5D=Presse-+und+Informationsamt+des+Landes+Berlin&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Bildung%2C+Jugend+und+Familie&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Finanzen&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Inneres%2C+Digitalisierung+und+Sport&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Integration%2C+Arbeit+und+Soziales&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Justiz%2C+Vielfalt+und+Antidiskriminierung&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Kultur+und+Europa&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Stadtentwicklung%2C+Bauen+und+Wohnen&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Umwelt%2C+Mobilit%C3%A4t%2C+Verbraucher-+und+Klimaschutz&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Wirtschaft%2C+Energie+und+Betriebe&institutions%5B%5D=Senatsverwaltung+f%C3%BCr+Wissenschaft%2C+Gesundheit%2C+Pflege+und+Gleichstellung']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for i in soup.select(' tbody tr'):
            try:
                ssd = i.td.text.strip().split('.')
                time_ = ssd[-1] + '-' + ssd[1] + '-' + ssd[0] + ' 00:00:00'
                if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
                    meat = {'title_': i.select_one(' td:nth-child(2)').text.strip(), 'time_': time_, 'category1_': 'pressemitteilungen', 'abstract_': i.select_one(' td:nth-child(3)').text.strip()}
                    yield Request('https://www.berlin.de'+i.a['href'], callback=self.parse_item, meta=meat)
            except:
                pass
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(time_) >= int(OldDateUtil.time):
            yield Request('https://www.berlin.de'+soup.select_one(' .pager-next a')['href'])

    def parse_item(self, response):
        item = NewsItem(language_id=self.language_id)
        soup = BeautifulSoup(response.text, 'html.parser')
        item['title'] = response.meta['title_']
        item['category1'] = response.meta['category1_']
        item['category2'] = None
        item['body'] = soup.select_one(' .textile').text.strip('\n')
        item['abstract'] = response.meta['abstract_']
        item['pub_time'] = response.meta['time_']
        item['images'] = []
        yield item
