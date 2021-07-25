import scrapy
from scrapy.http import HtmlResponse
import re

from jobparser.items import JobparserItem
from jobparser.selectors import HH_ITEM_SELECTORS, HH_NAVIGATION_SELECTORS


class HhruSpider(scrapy.Spider):
    name = "hhru"
    allowed_domains = ["hh.ru"]
    start_urls = [
        "https://omsk.hh.ru/search/vacancy"
        "?area=&fromSearchLine=true&st=searchVacancy&text=python"
    ]

    def parse(self, response: HtmlResponse):
        item_urls = response.xpath(HH_NAVIGATION_SELECTORS["parse_item"]).getall()
        for link in item_urls:
            yield response.follow(link, callback=self.parse_item)


        next_page = response.xpath(HH_NAVIGATION_SELECTORS['parse']).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_item(self, response: HtmlResponse):
        item = JobparserItem()
        for key, xpath in HH_ITEM_SELECTORS.items():
            item[key] = response.xpath(xpath)

        item["title"] = item["title"].get()
        item["salary"] = item["salary"].get()
        item["url"] = response.url
        item["_id"] = int(re.split('vacancy/|\?', item["url"])[1])

        yield item
