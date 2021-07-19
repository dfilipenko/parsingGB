import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "VKparser"
MONGO_COLL = "Tokiofashion"

DRIVER_PATH = "./chromedriver"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

url = 'https://vk.com/tokyofashion'

search_key = 'платье'
class TokyoScraper:

    def __init__(self, url, search_key, host, port, db_name, coll_name, driver_path, options):
        self.url = url
        self.search_key = search_key
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[coll_name]
        self.driver = webdriver.Chrome(driver_path, options=options)
        self.driver.get(self.url)

    def add_post_in_db(self, post):
        n = self.collection.find({"href": post["href"]})
        if len(list(n)) > 0:
            self.collection.update_one(post)
        else:
            self.collection.insert_one(post)

    def search(self):
        time.sleep(2)
        search_icon_xpath = "//a[contains(@class, 'ui_tab_search')]"
        search_icon = self.driver.find_element_by_xpath(search_icon_xpath)
        time.sleep(2)
        search_icon.click()
        search_field_xpath = '//input[contains(@class, "ui_search_field _field")]'
        search_field = self.driver.find_element_by_xpath(search_field_xpath)
        search_field.send_keys(self.search_key)
        search_field.send_keys(Keys.ENTER)
        time.sleep(2)
        self.scroll()

    def scroll(self):
        posts_xpath = "//div[contains(@class, 'post--with-likes')]"
        post_list = self.driver.find_elements_by_xpath(posts_xpath)
        last_post = post_list[-1]
        post_list_new = []
        while len(post_list) != len(post_list_new):
            time.sleep(2)
            actions = ActionChains(self.driver)
            actions.move_to_element(last_post)
            actions.perform()
            post_list = post_list_new
            try:
                register_window = self.driver.find_element_by_class_name("box_layout")
                skip_link_xpath = '//a[contains(@class, "JoinForm__notNow")]'
                skip_link = self.driver.find_element_by_xpath(skip_link_xpath)
                skip_link.click()
                post_list_new = self.driver.find_elements_by_xpath(posts_xpath)
                last_post = post_list_new[-1]

            except:
                time.sleep(2)
                post_list_new = self.driver.find_elements_by_xpath(posts_xpath)
                last_post = post_list_new[-1]
        return self.get_post_info(post_list)

    def get_post_info(self, post_list):
        for post in post_list:
            post_info = {}
            date_xpath = './/div[contains(@class, "post_date")]//span[contains(@class, "rel_date")]'
            date_str = post.find_element_by_xpath(date_xpath).get_attribute('textContent')
            date = date_str.replace('\xa0', ' ')
            post_info['date'] = date
            text_xpath = './/div[contains(@class, "wall_post_text")]'
            text = post.find_element_by_xpath(text_xpath).get_attribute('textContent')
            post_info['text'] = text
            href = post.get_attribute('data-post-id')
            post_info['href'] = 'https://vk.com/tokyofashion?w=wall' + href
            like_repost_xpath = f'.//div[contains(@class, "_like_wall{href}")]//a'
            like_repost = post.find_elements_by_xpath(like_repost_xpath)
            post_info['like'] = like_repost[0].get_attribute('data-count')
            post_info['repost'] = like_repost[1].get_attribute('data-count')
            views_xpath = f'.//div[contains(@class, "_like_wall{href}")]//div[contains(@class, "like_views")]'
            views = post.find_element_by_xpath(views_xpath)
            post_info['views'] = views.get_attribute('title')
            self.add_post_in_db(post_info)


tokyoposts = TokyoScraper(url, search_key, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL, DRIVER_PATH, options)
tokyoposts.search()