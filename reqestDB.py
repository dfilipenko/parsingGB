from pymongo import MongoClient

from InstaParser.settings import MONGO_HOST, MONGO_PORT

client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client.InstaParser
collection = db["instagram"]
username_for_search = input("Введите имя пользователя")
def get_in_followers(username, collection):
    user_in_followers = collection.find({"in_follower": username})
    username_in_followers = []
    for i in list(user_in_followers):
        username = i["username"]
        username_in_followers.append(username)
    return print(username_in_followers)

def get_out_followers(username, collection):
    user_out_followers = collection.find({"out_follower": username})
    username_out_followers = []
    for i in list(user_out_followers):
        username = i["username"]
        username_out_followers.append(username)
    return print(username_out_followers)

get_in_followers(username_for_search, collection)
get_out_followers(username_for_search, collection)