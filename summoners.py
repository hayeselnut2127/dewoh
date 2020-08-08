import pickle
import json

FILENAME = "summoners.json"

def save_summoners(data):
    with open(FILENAME, "w") as outfile:
        json.dump(data, outfile)

def load_summoners():
    with open(FILENAME, "r") as infile:
        return json.load(infile)