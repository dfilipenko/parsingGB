# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
import pymongo

from InstaParser.settings import MONGO_HOST, MONGO_PORT

class InstaparserPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        self.db = self.client.InstaParser

    def process_item(self, item, spider):
        n = self.db[spider.name].find({
            'user_id': item['user_id'],
            'in_follower': item['in_follower'],
            'out_follower': item['out_follower'],
            })
        try:
            if len(list(n)) > 0:
                self.db[spider.name].update_one(item)
            else:
                self.db[spider.name].insert_one(item)
        except Exception as e:
            print(e)

        return item

        # closing database conection on closing spider

    def close_spider(self):
        self.client.close()