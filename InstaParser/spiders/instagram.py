import copy
import json
import re
from urllib.parse import quote

import scrapy
from scrapy.http import HtmlResponse

from InstaParser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    template_user_url = "/%s"

    def __init__(self, login, password, **kwargs):
        super().__init__(**kwargs)
        self.login = login
        self.enc_password = password
        self.str_user_to_parse = input("Введите имена пользователей для парсинга через пробел")
        self.users_to_parse = self.str_user_to_parse.split()

    def fetch_csrf_token(self, text):
        matched = re.search('"csrf_token":"\\w+"', text).group()
        return matched.split(":").pop().replace(r'"', "")


    def parse(self, response: HtmlResponse):
        token = self.fetch_csrf_token(response.text)
        x_instagram_ajax = self.fetch_x_instagram_ajax(response.text)
        yield scrapy.FormRequest(
            url=self.login_url,
            method="POST",
            formdata={
                "username": self.login,
                "enc_password": self.enc_password,
            },
            headers={
                "X-CSRFToken": token,
                "x-ig-app-id": "936619743392459",
                "x-instagram-ajax": x_instagram_ajax,
            },
            callback=self.user_login,
        )

    def user_login(self, response: HtmlResponse):
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print("Json decode error")
            print(e)
            return
        except Exception as e:
            print(e)
            return

        if data["authenticated"]:
            for user in self.users_to_parse:
                yield response.follow(
                    self.template_user_url % copy.deepcopy(user),
                    callback=self.parse_following,
                    cb_kwargs={"username": copy.deepcopy(user)}
                )

    def parse_following(self, response: HtmlResponse, username: str):
        user_id = self.fetch_user_id(response.text, username)
        url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&search_surface=follow_list_page"
        yield response.follow(
            url,
            callback=self.get_followers_info,
            headers={
                "x-ig-app-id": "936619743392459",
            },
            cb_kwargs={
                "user_id": user_id,
                "username": copy.deepcopy(username)
                }
        )

    def get_followers_info(self, response: HtmlResponse, user_id: str, username: str):
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print("Json decode error")
            print(e)
            return
        except Exception as e:
            print(e)
            return


        try:
            users = data["users"]
        except AttributeError as e:
            print("Error during getting page_info")
            print(e)
            return
        except KeyError as e:
            print("Error during getting page_info")
            print(e)
            return

        for user in users:
            item = InstaparserItem()
            item["user_id"] = user["pk"]
            item["username"] = user["username"]
            item["full_name"] = user["full_name"]
            item["profile_pic_url"] = user["profile_pic_url"]
            item["in_follower"] = username
            item["out_follower"] = None
            yield item

        if data["big_list"]:
            next_max_id = data["next_max_id"]
            url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&max_id={next_max_id}&search_surface=follow_list_page"
            yield response.follow(
                url,
                callback=self.get_followers_info,
                headers={
                    "x-ig-app-id": "936619743392459",
                },
                cb_kwargs={
                    "user_id": user_id,
                    "username": copy.deepcopy(username)
                }
            )
        else:
            url = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12"
            yield response.follow(
                url,
                callback=self.get_following_info,
                headers={
                    "x-ig-app-id": "936619743392459",
                },
                cb_kwargs={
                    "user_id": user_id,
                    "username": copy.deepcopy(username)
                }
            )

    def get_following_info(self, response: HtmlResponse, user_id: str, username: str):

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print("Json decode error")
            print(e)
            return
        except Exception as e:
            print(e)
            return


        try:
            users = data["users"]
        except AttributeError as e:
            print("Error during getting page_info")
            print(e)
            return
        except KeyError as e:
            print("Error during getting page_info")
            print(e)
            return

        for user in users:
            item = InstaparserItem()
            item["user_id"] = user["pk"]
            item["username"] = user["username"]
            item["full_name"] = user["full_name"]
            item["profile_pic_url"] = user["profile_pic_url"]
            item["out_follower"] = username
            item["in_follower"] = None
            yield item

        if data["big_list"]:
            next_max_id = data["next_max_id"]
            url = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12&max_id={next_max_id}"
            yield response.follow(
                url,
                callback=self.get_following_info,
                headers={
                    "x-ig-app-id": "936619743392459",
                },
                cb_kwargs={
                    "user_id": user_id,
                    "username": copy.deepcopy(username)
                }
            )


    def fetch_x_instagram_ajax(self, text):
        matched = re.search('"rollout_hash":"\\w+"', text).group()
        return matched.split(":").pop().replace(r'"', "")

    def fetch_user_id(self, text, username):
        matched = re.search('{"id":"\\d+","username":"%s"}' % username, text).group()
        return json.loads(matched).get("id")