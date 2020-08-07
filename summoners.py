import pickle
import json

FILENAME = "summoners.json"

SUMS = {'Hayeselnut': 'AfQpFNTK5bMPG57M0B5p-JskZyUb4up_xrqBy4LArJMdUzU', 'eZED': 'd75ZuXWRniQNfwvLwcT9SjPBA8HIgjIEAC5S9kCBvW0WaHI', 'MARKERAD': 'dx8hGVxux5GoxiX8T14iy1J0-QG8-U9eclJZaUxXbc-w7Zw', 'Fruit Loops': 'iOiRv66I7lmJRpWSDdFTb2ArR_XN211MT2GT_a2_UcceP0E', 'PicklesPops': '9lupLZVWpFLXuol5qnNj5TZn1-bJlpCm05mS_qqNqmsWB6A', 'Yur Faddur': '3DNWHJ__FLoK6KyPJiNKGpbImRKAhLGV-OgCrGQcLR7S-28', 'eZed': 'd75ZuXWRniQNfwvLwcT9SjPBA8HIgjIEAC5S9kCBvW0WaHI'}

def save_summoners(data):
    with open(FILENAME, "w") as outfile:
        json.dump(data, outfile)

def load_summoners():
    with open(FILENAME, "r") as infile:
        return json.load(infile)