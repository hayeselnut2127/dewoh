import requests
import urllib
import json

url = "http://ddragon.leagueoflegends.com/cdn/10.16.1/data/en_US/champion.json"

NOT_FOUND = {
    # "queueId": -1,
    # "map": "n/a",
    # "description": "n/a",
    # "notes": "n/a",
}

def find_champion(champion_id):
    champions = requests.get(url).json()

    for c in champions["data"]:
        print (champions["data"][c]["key"], c)

        if champions["data"][c]["key"] == champion_id:
            return champions["data"][c]

    return NOT_FOUND