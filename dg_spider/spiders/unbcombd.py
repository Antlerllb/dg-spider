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


class UnbcombdSpider(BaseSpider):
    name = 'unbcombd'
    website_id = 2274
    language_id = 1779
    author = '王晋麟'

    time_judge = [True, True]
    flag = [['17', '19', '16', '20', '14', '18', '21', '22', '15', '25', '27'], ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '14']]
    ind = [0, 0]
    lan_id = [1866, 1779]
    bases_url = ['https://www.unb.com.bd/api/categories-news?category_id={}&item={}', 'https://unb.com.bd/api/categories-news-bn?category_id={}&item={}']

    def start_requests(self):
        for i in range(len(self.bases_url)):
            yield Request(url=self.bases_url[i].format(self.flag[i][self.ind[i]], 1), callback=self.parse, meta={'page': 1, 'lan': i})

    def parse(self, response):
        js = response.json()
        change_page = True
        if js['hasMore']:
            soup = BeautifulSoup(js['html'], 'html.parser')
            news_lis = soup.select('.hidden-xs .news-block-four')
            for news in news_lis:
                news_url = news.select('.content-inner h3 a')[0].attrs['href']
                if self.time_judge[response.meta['lan']]:
                    yield Request(url=news_url, callback=self.parse_item, meta={'lan': response.meta['lan']})
                else:
                    change_page = False
                    break
            if change_page:
                yield Request(url=self.bases_url[response.meta['lan']].format(self.flag[response.meta['lan']][self.ind[response.meta['lan']]], response.meta['page'] + 1),
                              callback=self.parse, meta={'page': response.meta['page'] + 1, 'lan': response.meta['lan']})
            else:
                self.time_judge[response.meta['lan']] = True
                self.ind[response.meta['lan']] += 1
                if self.ind[response.meta['lan']] < len(self.flag[response.meta['lan']]):
                    yield Request(url=self.bases_url[response.meta['lan']].format(self.flag[response.meta['lan']][self.ind[response.meta['lan']]], 1), callback=self.parse,
                                  meta={'page': 1, 'lan': response.meta['lan']})

        else:
            self.time_judge[response.meta['lan']] = True
            self.ind[response.meta['lan']] += 1
            if self.ind[response.meta['lan']] < len(self.flag[response.meta['lan']]):
                yield Request(
                    url=self.bases_url[response.meta['lan']].format(self.flag[response.meta['lan']][self.ind[response.meta['lan']]], 1),
                    callback=self.parse,
                    meta={'page': 1, 'lan': response.meta['lan']})

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        mod = re.compile('\d+, \d+, \d+:\d+')
        lis = [t.text.strip() for t in soup.select('.content .upper-box ul li')]
        time = []
        for t in lis:
            if len(re.findall(mod, t)) != 0:
                time = t.replace(',', '').replace('Publish-', '').strip().split(' ')
                break
        if time[4] == 'PM':
            t = time[3].split(':')
            time[3] = str(int(t[0]) % 12 + 12) + ':' + t[1]
        pub_time = '{}-{:0>2s}-{:0>2s} {}:00'.format(time[2], str(OldDateUtil.EN_1866_DATE[time[0]]).zfill(2), time[1], time[3])
        if OldDateUtil.time is None or OldDateUtil.time <= OldDateUtil.str_datetime_to_timestamp(pub_time):
            item = NewsItem(language_id=self.language_id)
            item['body'] = '\n'.join(
                [' '.join(content.text.replace('\xa0', '').replace('\n', '').strip().split()) for content in
                 soup.select('.content .text .news-article-text-block p') if content.text.strip() != ''])
            if item['body'] == '':
                pass
            else:
                item['category1'] = soup.select('.content .upper-box ul:nth-child(1) li')[1].text
                item['title'] = soup.select('.content .upper-box h2')[0].text.strip()
                item['pub_time'] = pub_time
                item['language_id'] = self.lan_id[response.meta['lan']]
                item['images'] = [img.select('img')[0].attrs['src'].strip() for img in soup.select('.content .image') if
                                  len(img.select('img')) != 0]
                item['abstract'] = item['body'].split('\n')[0].strip() if item['body'].split('\n')[0] != '' and len(
                    item['body'].split('\n')[0]) < 200 else item['body'].split('.')[0].strip() + '.'
                if len(item['body'].split('\n')) == 1:
                    item['body'] = item['abstract'].strip() + '\n' + item['body'].strip()
                yield item
        else:
            self.time_judge[response.meta['lan']] = False
