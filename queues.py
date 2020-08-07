import requests
import urllib
import json

url = "http://static.developer.riotgames.com/docs/lol/queues.json"

NOT_FOUND = {
    "queueId": -1,
    "map": "n/a",
    "description": "n/a",
    "notes": "n/a",
}

def find_queue(queue_id):
    queues = requests.get("http://static.developer.riotgames.com/docs/lol/queues.json").json()

    for q in queues:
        if q["queueId"] == queue_id:
            return q

    return NOT_FOUND