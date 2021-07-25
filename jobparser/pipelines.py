# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo

from jobparser.settings import MONGO_HOST, MONGO_PORT

# from itemadapter import ItemAdapter


class JobparserPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        self.db = self.client.vacancies

    def process_salary(self, salary):
        if type(salary) == str:
            salary = salary.replace('\xa0', '').split()
            currency = salary[-1]
        else:
            currency = (salary[-1].split('\xa0'))[-1]
            salary = ''.join(salary).replace('\xa0', '').replace(currency, '')

        if 'oт' and 'до' in salary:
            salary_min = int(salary[1])
            salary_max = int(salary[3])
        elif 'от' in salary and 'до' not in salary:
            salary_max = None
            try:
                salary_min = int(salary.split('от')[1])
            except:
                salary_min = int(salary[1])
        elif 'до' in salary and 'от' not in salary:
            salary_min = None
            try:
                salary_max = int(salary.split('до')[1])
            except:
                salary_max = int(salary[1])
        elif '-' in salary:
            k = salary.split('-')
            salary_min = int(k[0])
            salary_max = int(k[1])
        else:
            salary_min = None
            salary_max = None
            currency = None

        return salary_min, salary_max, currency


    def process_item(self, item, spider):
        # print("Inside pipeline")
        # print()
        s_min, s_max, currency = self.process_salary(item["salary"])
        item["salary_min"], item["salary_max"], item["currency"] = s_min, s_max, currency

        del item["salary"]

        item["source"] = spider.name

        n = self.db[spider.name].find({"url": item["url"]})
        if len(list(n)) > 0:
            self.db[spider.name].update_one(item)
        else:
            self.db[spider.name].insert_one(item)

        return item

    # closing database conection on closing spider
    def close_spider(self):
        self.client.close()
