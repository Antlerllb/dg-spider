


from bs4 import BeautifulSoup
import scrapy
from dg_spider.items import NewsItem
import scrapy
from dg_spider.libs.base_spider import BaseSpider
from dg_spider.utils.old_utils import OldDateUtil



class VayofmSpider(BaseSpider):
    name = 'vayofm'
    website_id = 2692
    language_id = 2275
    lan_num = 1
    author = '蔺康天'
    start_urls = ["https://www.vayofm.com/"]

    def parse(self, response):

        soup = BeautifulSoup(response.text, 'html.parser')
        tag_list = soup.find_all("li", class_="nav-item dropdown")
        for tag in tag_list:
            cat = tag.find_all("a")[0].string
            c2_list = tag.find_all("a", class_="dropdown-item")
            for c2 in c2_list:
                href = c2['href']
                if href=="index1.php?option=list&id=149":
                    href="https://www.vayofm.com/"+href
                yield scrapy.Request(url=href, callback=self.parse2, meta={"c1": cat})

    def parse2(self, response):
        now_url = response.url + "&paginate="
        soup = BeautifulSoup(response.text, 'html.parser')
        nextt = soup.find_all("ul", class_="pagination font-content")[0]
        nl = nextt.find_all("a")[-2]
        max_page = int(nl.string)
        for i in range(1, 5):
            next_url = now_url + str(i)
            yield scrapy.Request(url=next_url, callback=self.parse3, meta=response.meta)

    def parse3(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = soup.find_all("div", class_="news-ctn-list")
        for news in news_list:
            href = news.find_all("a")[0]['href']
            img = news.find_all("img")[0].get('src')
            abstract = news.find_all("a")[1].text
            cat = response.meta["c1"]
            yield scrapy.Request(url=href, callback=self.parse4, meta={"img": img, "abstract": abstract, "cat": cat})

    def parse4(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        time = soup.find_all("div", class_="col-sm-9 col-xs-8")[0].text.split(" ")
        for i in time:
            if '-' in i:
                pub = i.split('-')
                pub_time1 = f"{pub[2]}-{pub[1]}-{pub[0]} "
        pub_time1 = pub_time1 + "00:00:00"
        b = soup.find_all("p")
        body = ""
        for i in b:
            body += i.text.replace('\n', '')
            body += '\n'
        ans = ""
        if OldDateUtil.time is not None and OldDateUtil.str_datetime_to_timestamp(pub_time1) < OldDateUtil.time:
            return
        item = NewsItem(language_id=self.language_id)
        body = body.replace('\xa0', '').replace('\u200b', '').replace('\r', '').replace('\n', '').replace('\t','').strip()
        for i in body:
            ans += i.replace('', '')
            ans += '\n'
        abb = ""
        abs = response.meta["abstract"].replace("\xa0", "").replace("\u200b", "").strip()
        for i in abs:
            abb += i
        ans=response.meta["abstract"].replace('\xa0', '').replace("\u200b", "").replace('\r','').replace('\n','').replace('\t', '').strip()+'\n'+ans
        item["body"] = ans
        item["title"] = response.meta["abstract"].replace('\xa0', '').replace("\u200b", "").replace('\r', '').replace('\n', '').replace('\t', '').strip()
        item["abstract"] = response.meta["abstract"].replace('\xa0', '').replace("\u200b", "").replace('\r','').replace('\n','').replace('\t', '').strip()
        item["category1"] = response.meta["cat"]
        item["pub_time"] = pub_time1
        img_list = []
        img_list.append(response.meta['img'])
        yield item


