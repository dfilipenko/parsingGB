# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Compose, MapCompose, TakeFirst

def apply_selector(text):
    sel = scrapy.Selector(text=text)
    feature = {}
    feature_name = sel.xpath('//dt[@class="def-list__term"]/text()').get()
    feature_value = sel.xpath('//dd[@class="def-list__definition"]/text()').get().strip()
    feature[feature_name] = feature_value
    yield feature

def get_features(text):
    b = {}
    for i in text:
        b.update(i)
    return b

def get_int(text):
    price = int(text[0].replace(" ", ""))
    return price


class StroyparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(get_int), output_processor=TakeFirst())
    features = scrapy.Field(input_processor=MapCompose(apply_selector), output_processor=Compose(get_features))
    img_urls = scrapy.Field()
    img_info = scrapy.Field()
    _id = scrapy.Field()

