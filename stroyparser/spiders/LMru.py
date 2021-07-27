import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from stroyparser.items import StroyparserItem
from stroyparser import settings

custom_settings = { "ITEM_PIPELINES": {'scrapy.pipelines.images.StroyImagesPipeline': 1}, "IMAGES_STORE": "images"}

class LmruSpider(scrapy.Spider):
    name = 'LMru'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://nizhniy-novgorod.leroymerlin.ru/catalogue/elektricheskie-vodonagrevateli-nakopitelnye/']

    def parse(self, response: HtmlResponse):
        links = response.xpath('//a[contains(@class, "iypgduq_plp ")]/@href')
        for link in links:
            yield response.follow(link, callback=self.parse_item)

        # next_page = response.xpath('//a[contains(@data-qa-pagination-item, "right")]/@href').get()
        # if next_page:
        #     yield response.follow(next_page, callback=self.parse)


    def parse_item(self, response: HtmlResponse):
        # get only the first element with this xpath
        price_xpath = '//uc-pdp-price-view//span[@slot="price"]/text()'
        name_xpath = "//h1/text()"
        # big_image_xpath = '//div[contains(@class, ' \
        #                   '"js-gallery-img-frame")]//img/@src'
        big_image_xpath = '//uc-pdp-media-carousel[@slot="media-content"]/picture/img/@src'

        feature_xpath = '//dl[@class="def-list"]/div[@class="def-list__group"]'

        # item = AvitoscraperItem()
        # item['name'] = response.xpath(name_xpath).get()
        # item['price'] = response.xpath(price_xpath).get()
        # item['img_urls'] = response.xpath(small_image_xpath).getall()
        # yield item

        loader = ItemLoader(item=StroyparserItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_xpath("name", name_xpath)
        loader.add_xpath("price", price_xpath)
        loader.add_xpath("img_urls", big_image_xpath)
        loader.add_xpath("features", feature_xpath)

        yield loader.load_item()
