from dotenv import load_dotenv
import os
import requests
from pprint import pprint

load_dotenv("C:/Users/dfili/PycharmProjects/parsingGB/.env")
key = "API_key"
API_key = os.getenv(key, None)

city_name = input('Введите название города ')

def wether_in_city(city_name):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}'
    response = requests.get(url)

    return pprint(response.json())

wether_in_city(city_name)