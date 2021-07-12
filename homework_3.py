import json
import time
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

vacancy = input('Введите название вакансии: ')

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "HeadHanter"
MONGO_COLL = f"vacancies_{vacancy}"

ENDPOINT_URL = "https://nn.hh.ru/search/vacancy"
PARAMS = {
    "area": "66",
    "clusters": "true",
    "enable_snippets": "true",
    "st": "searchVacancy",
    "text": vacancy,

}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}

class HhScraper:
    def __init__(self, start_url, params, headers, host, port, db_name, coll_name):
        self.start_url = start_url
        self.start_params = params
        self.headers = headers
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[coll_name]
        self.info_about_vacancies = []

    def get_html_string(self, url, params, headers):
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except Exception as e:
            time.sleep(1)
            print(e)
            return None
        return response.text


    @staticmethod
    def get_dom(html_string):
        return BeautifulSoup(html_string, "html.parser")

    def run(self):
        html_string = self.get_html_string(self.start_url, self.start_params, self.headers)
        soup = HhScraper.get_dom(html_string)
        def find_vacancies(html):
            vacancies = soup.find_all("div",
                                      attrs={"class": "vacancy-serp-item"}
                                      )
            for vacancy in vacancies:
                info = self.get_info_from_vacancy(vacancy)
                self.info_about_vacancies.append(info)
                self.collection.insert_one(info)
        next_link = soup.find("a", attrs={"class": "bloko-button", "data-qa": "pager-next"})

        while next_link != None:
            find_vacancies(soup)
            next = next_link.attrs["href"]
            page_number = int(next.split("page=")[1])
            params = self.start_params
            params["page"] = page_number
            html_string = self.get_html_string(self.start_url, params, self.headers)
            soup = HhScraper.get_dom(html_string)
            next_link = soup.find("a", attrs={"class": "bloko-button", "data-qa": "pager-next"})

        self.client.close()
        return self.info_about_vacancies

    def get_info_from_vacancy(self, vacancy):
        info = {}
        info["name"] = vacancy.find("span",
            attrs={"class": "resume-search-item__name"}
        ).text
        try:
            salary = vacancy.find("span",
                attrs={
                    "data-qa": "vacancy-serp__vacancy-compensation",
                    'class': "bloko-section-header-3 bloko-section-header-3_lite"
                }
            ).text.replace('\u202f', '').split()
            if 'от' in salary:
                info["min_salary"] = int(salary[1])
            elif ' - ' in salary:
                info["min_salary"] = int(salary[0])
                info["max_salary"] = int(salary[2])
            elif 'до' in salary:
                info["max_salary"] = int(salary[1])
        except Exception:
            info["salary"] = None

        info["href"] = vacancy.find("a",
                                    attrs={
                                        "class": "bloko-link",
                                        "data-qa": "vacancy-serp__vacancy-title"
                                    }
                                    ).attrs["href"]
        info["source"] = "HH.ru"
        return info

    def save_info_about_vacance(self):
        with open(f"vacancy_hh_{vacancy}.json", 'w', encoding="utf-8") as file:
            json.dump(self.info_about_vacancies, file)




if __name__ == "__main__":
    scraper = HhScraper(ENDPOINT_URL, PARAMS, headers, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL)
    scraper.run()
    #scraper.save_info_about_vacance()