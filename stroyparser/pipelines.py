# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
import pymongo

from stroyparser.settings import MONGO_HOST, MONGO_PORT
from scrapy.pipelines.images import ImagesPipeline


class StroyImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        print("image")
        print()
        if item["img_urls"]:
            for img_link in item["img_urls"]:
                try:
                    yield scrapy.Request(img_link)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item["img_info"] = [x[1] for x in results if x[0]]
        if item["img_urls"]:
            del item["img_urls"]
        return item


class StroyparserPipeline:

    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        self.db = self.client.LMParser

    def process_item(self, item, spider):
        n = self.db[spider.name].find({'url': item['url']})
        print("process")
        print()
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
