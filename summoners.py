import pickle
import json

FILENAME = "summoners.json"

def save_summoners(ids):
    with open(FILENAME) as outfile:
        json.dump(ids, outfile)

def load_summoners():
    infile = open(FILENAME)
    s = json.load(infile)
    infile.close()

    return s