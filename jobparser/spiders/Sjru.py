import scrapy
from scrapy.http import HtmlResponse
import re

from jobparser.items import JobparserItem
from jobparser.selectors import SJ_ITEM_SELECTORS, SJ_NAVIGATION_SELECTORS

class SjruSpider(scrapy.Spider):
    name = 'Sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://nn.superjob.ru/vacancy/search/?keywords=python']

    def parse(self,  response: HtmlResponse):
        item_urls = response.xpath(SJ_NAVIGATION_SELECTORS["parse_item"]).getall()
        for link in item_urls:
            yield response.follow(link, callback=self.parse_item)

        next_page = response.xpath(SJ_NAVIGATION_SELECTORS['parse']).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response: HtmlResponse):
        item = JobparserItem()
        for key, xpath in SJ_ITEM_SELECTORS.items():
            item[key] = response.xpath(xpath)

        item["title"] = ''.join(item["title"].getall())
        item["salary"] = item["salary"].getall()
        item["url"] = response.url
        item["_id"] = int(re.split('\-|\.', item["url"])[-2])

        yield item