from urllib.parse import quote_plus

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from stroyparser import settings
from stroyparser.spiders.LMru import LmruSpider

if __name__ == "__main__":
    custom_settings = Settings()
    custom_settings.setmodule(settings)

    #query = quote_plus("видеокарта NVIDIA".encode(encoding="cp1251"))

    process = CrawlerProcess(settings=custom_settings)
    process.crawl(LmruSpider)  #query=query
    # process.crawl(AvitoSpider)

    process.start()