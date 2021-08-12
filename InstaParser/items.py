# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    full_name = scrapy.Field()
    profile_pic_url = scrapy.Field()
    in_follower = scrapy.Field()
    out_follower = scrapy.Field()

