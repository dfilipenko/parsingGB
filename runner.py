import os

from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from InstaParser import settings
from InstaParser.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    load_dotenv(".env")
    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    #user_to_parse = "nachalkaschool"

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    kwargs = {
        "login": login,
        "password": password,
        #"user_to_parse": user_to_parse,
    }
    process.crawl(InstagramSpider, **kwargs)

    process.start()
