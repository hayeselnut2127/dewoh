import requests
import urllib
import json

url = "http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json"

NOT_FOUND = {
    "version": "n/a",
    "id": "n/a",
    "key": "n/a",
    "name": "n/a",
    "title": "n/a",
    "blurb": "n/a",
    "info": "n/a",
    "image": "n/a",
    "tags": "n/a",
    "partype": "n/a",
    "stats": "n/a",
}

def find_champion(champion_id):
    champions = requests.get(url).json()

    for c in champions["data"]:
        if champions["data"][c]["key"] == champion_id:
            return champions["data"][c]

    return NOT_FOUND