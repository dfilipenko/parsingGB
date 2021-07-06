import requests

import json

user = input('Введите имя пользователя ')

def save_repos_info(response, path=f'repo for {user}'):
    with open(path, "w") as f:
        json.dump(response, f)


def repo_for_user(user, path=f'repo for {user}'):
    url = f"https://api.github.com/users/{user}/repos"
    response = requests.get(url)
    response = response.json()
    save_repos_info(response)
    repo_list = []
    for d in response:
        repo = d.get('name')
        repo_list.append(repo)

    return print(repo_list)

repo_for_user(user)