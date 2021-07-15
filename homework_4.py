import requests
from lxml.html import fromstring
from pymongo import MongoClient

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "News"
MONGO_COLL = "News_from_mail_yandex_lenta"

mail_url = 'https://news.mail.ru/'

lenta_url = 'https://lenta.ru/'

yandex_url = 'https://yandex.ru/news/?utm_source=main_stripe_big'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class NewsScraper:

    def __init__(self, headers, host, port, db_name, coll_name):
        self.headers = headers
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[coll_name]

    #@staticmethod
    def add_news_in_db(self, news):
        self.collection.insert_one(news)

    def is_exists(self, news):
        n = self.collection.find({"href": news["href"]})
        return len(list(n))

    def parsing_mail_ru(self):
        mail_url = 'https://news.mail.ru/'
        response = requests.get(mail_url, self.headers)
        dom = fromstring(response.text)
        html_news_xpath = '//ul[contains(@class, "js-module")]//a[@href]/@href'
        news_html_list = list(dom.xpath(html_news_xpath))
        for news in news_html_list:
            news_info = {}
            item_response = requests.get(news, headers=headers)
            item_dom = fromstring(item_response.text)
            news_title = '//div[contains(@class,"js-article")]//h1/text()'
            news_source = '//div[contains(@class,"js-article")]//span[@class="link__text"]/text()'
            news_date = '//div[contains(@class,"js-article")]//span[contains(@class, "js-ago")]/@datetime'
            news_info['source'] = item_dom.xpath(news_source)[0]
            news_info['title'] = item_dom.xpath(news_title)[0]
            news_info['href'] = news
            news_info['date'] = item_dom.xpath(news_date)[0]
            if self.is_exists(news_info) > 0:
                continue
            else:
                self.add_news_in_db(news_info)

    def parsing_lenta_ru(self):
        lenta_url = 'https://lenta.ru/'
        response = requests.get(lenta_url, self.headers)
        dom = fromstring(response.text)
        lenta_item_xpath = '//section[contains(@class, "js-top-seven")]//a[contains(time, @class)]'
        for news in dom.xpath(lenta_item_xpath):
            news_info = {}
            news_title = './text()'
            news_href = './@href'
            news_date = './time/@datetime'
            news_info['source'] = 'lenta.ru'
            news_info['title'] = news.xpath(news_title)[0]
            news_info['href'] = lenta_url + news.xpath(news_href)[0]
            news_info['date'] = news.xpath(news_date)[0]
            if self.is_exists(news_info) > 0:
                continue
            else:
                self.add_news_in_db(news_info)

    def parsing_yandex(self):
        yandex_url = 'https://yandex.ru/news/?utm_source=main_stripe_big'
        response = requests.get(yandex_url, self.headers)
        dom = fromstring(response.text)
        yandex_item_xpath = '//div[contains(@class, "news-top-flexible-stories")]/div[contains(@class, "mg-grid__col")]'
        for news in dom.xpath(yandex_item_xpath):
            news_info = {}
            news_title = './/h2/text()'
            news_href = './/a[contains(@class, "mg-card__link")]/@href'
            news_date = './/span[@class="mg-card-source__time"]/text()'
            news_source = './/span[@class="mg-card-source__source"]/a/text()'
            news_info['source'] = news.xpath(news_source)[0]
            news_info['title'] = news.xpath(news_title)[0]
            news_info['href'] = news.xpath(news_href)[0]
            news_info['date'] = news.xpath(news_date)[0]
            if self.is_exists(news_info) > 0:
                continue
            else:
                self.add_news_in_db(news_info)

mailscraper = NewsScraper(headers, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL)
mailscraper.parsing_mail_ru()
mailscraper.parsing_lenta_ru()
mailscraper.parsing_yandex()