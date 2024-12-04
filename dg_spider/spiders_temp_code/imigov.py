


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

li=[]
e_month={
        'January':'01',
        'February':'02',
        'March':'03',
        'April':'04',
        'May':'05',
        'June':'06',
        'July':'07',
        'August':'08',
        'September':'09',
        'October':'10',
        'November':'11',
        'December':'12'
}


class imigovSpider(BaseSpider):#..一共就只有五条新闻，本来公告也打算作为新闻写进去，但是公告都只有标题内容非常奇怪所以没有爬
    name = 'imigov'
    website_id = 419
    language_id = 2036
    start_urls = ['https://www.imi.gov.my/index.php/en/news-announcement/']

# check: wpf pass
#aurhor：李沐潼

    def parse(self, response):
        soup = mutong(response.text, 'html.parser')
        meta={}
        meta['category1']=soup.select('.elementor-widget-container>h2')[0].text
        meta['category2']=soup.select('.elementor-widget-container>h2')[2].text
        next_url = soup.select('.elementor-pagination>a')[0].get('href')
        current_page_num = soup.select('.current')[0].text[-1]
        next_page_num = soup.select('.elementor-pagination>a')[0].text[-1]
        new_url = soup.select('h3>a')

        if current_page_num < next_page_num:
            yield Request(next_url, meta=meta, callback=self.parse)
        else:
            pass

        for j in new_url:
            yield Request(j.get('href'), meta=meta, callback=self.parse_items)






    def parse_items(self,response):
        soup = mutong(response.text, 'html.parser')

        ti = soup.select('.elementor-post-info__item--type-date')[0].text.strip()
        ti_li = ti.split(', ')
        pub_time = "{}-{}-{} 00:00:00".format(ti_li[1], e_month[ti_li[0].split(' ')[0]], ti_li[0].split(' ')[1])
        if OldDateUtil.time is None or OldDateUtil.str_datetime_to_timestamp(pub_time) >= int(OldDateUtil.time):
            item = NewsItem(language_id=self.language_id)
            item['category1']=response.meta['category1']
            item['category2'] = response.meta['category2']
            item['pub_time']=pub_time

            title = soup.select('.elementor-widget-container>h2')[0].text
            item['title']=title

            body_li1 = soup.select('.elementor-widget-container>p')
            body1 = ''.join([i.text for i in body_li1[:-3]])
            body_li2 = soup.select('.o9v6fnle')
            body2 = ''.join([i.text for i in body_li2])
            if len(body2)>len(body1):
                item['body']=body2
                abstract = body_li2[0].text
                item['abstract']=abstract
            else:
                item['body'] = body1
                abstract = body_li1[0].text
                item['abstract'] = abstract

            image_li = soup.select('figure>.gallery-icon>a>img')
            image=[]
            if image_li != []:
                for i in image_li:
                    image.append(i.get('data-src'))
            else:
                image_li = soup.select('.has_eae_slider>.elementor-widget-wrap>.elementor-element>.elementor-widget-container>img')
                for i in image_li:
                    if i.get('data-src')[-3:] == 'jpg':
                        image.append(i.get('data-src'))
            item['images']=image


            yield item


