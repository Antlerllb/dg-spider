from scrapy import Selector




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


class ThedailystarSpider(BaseSpider):
    name = 'thedailystar'
    website_id = 2269
    language_id = 1779
    author = '王晋麟'
    jg = [True, True]
    tps = [[], []]
    lan_id = [1779, 1866]

    @staticmethod
    def time_transform(string, mode):
        if mode == 1:
            return ''.join([str(OldDateUtil.BN_1779_DATE[string[i]]) for i in range(len(string))])
        elif mode == 2:
            return str(OldDateUtil.BN_1779_DATE[string])

    def start_requests(self):
        urls = ['https://bangla.thedailystar.net/', 'https://www.thedailystar.net/']
        for i in range(len(urls)):
            yield Request(url=urls[i], callback=self.parse, meta={'ind': i})

    def parse(self, response):
        sel = Selector(response)
        yield Request(url=response.urljoin(
            sel.css('#main-menu > li:not(.hide-topmenu)')[response.meta['ind']].css('a::attr(href)').get()),
                      callback=self.parse_again, meta={'ind': response.meta['ind']})

    def parse_again(self, response):
        sel = Selector(response)
        li_lists = sel.css('.mCustomScrollbar .sub-category-menu li')
        for li in li_lists:
            self.tps[response.meta['ind']].append((li.css('a::attr(href)').get(), li.css('a::text').get()))
        href, ct1 = self.tps[response.meta['ind']][0]
        yield Request(url=response.urljoin(href + '?page=0'), callback=self.parse_page,
                      meta={'category1': ct1, 'ind': 0, 'lan': response.meta['ind']})

    def parse_page(self, response):
        sel = Selector(response)
        for news in sel.css('.view-content .type-horizontal-list'):
            if self.jg[response.meta['lan']]:
                news_href = response.urljoin(news.css('.title a::attr(href)').get())
                title = news.css('.title a::text').get().strip()
                abstract = news.css('.intro::text').get().strip()
                yield Request(url=news_href, callback=self.parse_item, meta={'category1': response.meta['category1'],
                                                                             'title': title,
                                                                             'abstract': abstract,
                                                                             'lan': response.meta['lan']
                                                                             })
            else:
                break
        if self.jg[response.meta['lan']]:
            href = sel.css('.pager-show-more-next a::attr(href)').get()
            if href is not None:
                yield Request(url=response.urljoin(href), callback=self.parse_page,
                              meta={'category1': response.meta['category1'], 'ind': response.meta['ind'],
                                    'lan': response.meta['lan']})
            else:
                self.jg[response.meta['lan']] = True
                ind = response.meta['ind'] + 1
                if ind < len(self.tps):
                    href, ct1 = self.tps[response.meta['lan']][ind]
                    yield Request(url=response.urljoin(href), callback=self.parse_page,
                                  meta={'category1': ct1, 'ind': ind, 'lan': response.meta['lan']})
        else:
            self.jg[response.meta['lan']] = True
            ind = response.meta['ind'] + 1
            if ind < len(self.tps):
                href, ct1 = self.tps[response.meta['lan']][ind]
                yield Request(url=response.urljoin(href), callback=self.parse_page,
                              meta={'category1': ct1, 'ind': ind, 'lan': response.meta['lan']})

    def parse_item(self, response):
        sel = Selector(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        time = sel.css('.pane-news-details-left .date::text').get()
        if time is not None:
            if response.meta['lan'] == 0:
                time = time.strip().replace(',', '').split(' ')
                if time[5] == 'অপরাহ্ন':
                    t = time[4].split(':')
                    time[4] = str(int(self.time_transform(t[0], 1)) % 12 + 12) + ':' + self.time_transform(t[1], 1)
                else:
                    t = time[4].split(':')
                    time[4] = self.time_transform(t[0], 1) + ':' + self.time_transform(t[1], 1)
                pub_time = '{}-{:0>2s}-{:0>2s} {}:00'.format(self.time_transform(time[3], 1), str(OldDateUtil.BN_1779_DATE[time[1]]),
                                                             self.time_transform(time[2], 1), time[4])
            else:
                time = time.strip().replace(',', '').split(' ')
                if time[5] == 'PM':
                    t = time[4].split(':')
                    time[4] = str(int(t[0]) % 12 + 12) + ':' + t[1]
                pub_time = '{}-{:0>2s}-{:0>2s} {}:00'.format(time[3], str(OldDateUtil.EN_1866_DATE[time[1]]), time[2], time[4])
            if OldDateUtil.time is None or OldDateUtil.time <= OldDateUtil.str_datetime_to_timestamp(pub_time):
                item = NewsItem(language_id=self.language_id)
                item['body'] = '\n'.join(
                    [content.text.strip() for content in soup.select('.pane-node-content .pb-20 > p') if
                     content.text != ''])
                if item['body'].strip() != '':
                    item['language_id'] = self.lan_id[response.meta['lan']]
                    item['category1'] = response.meta['category1']
                    item['title'] = response.meta['title'] if response.meta['title'] != '' else sel.css(
                        '.pane-node-content *[itemprop="headline"]::text').get().strip()
                    item['pub_time'] = pub_time
                    if response.meta['lan'] == 0:
                        item['images'] = [img.css('img::attr(data-src)').get() for img in
                                          sel.css('.pane-node-content picture img:not(.ratio__1x1)')]
                    else:
                        item['images'] = [img.css('img::attr(data-srcset)').get() for img in
                                          sel.css('.pane-node-content picture img:not(.ratio__1x1)')]
                    item['abstract'] = response.meta['abstract'] if response.meta['abstract'] != '' else \
                    item['body'].split('\n')[0]
                    if len(item['body'].split('\n')) == 1:
                        item['body'] = item['abstract'].strip() + '\n' + item['body'].strip()
                    yield item
            else:
                self.jg[response.meta['lan']] = False
