import pickle

SUMMONER_IDS = {
    "Hayeselnut": "AfQpFNTK5bMPG57M0B5p-JskZyUb4up_xrqBy4LArJMdUzU",
    "eZED": "d75ZuXWRniQNfwvLwcT9SjPBA8HIgjIEAC5S9kCBvW0WaHI",
    "MARKERAD": "dx8hGVxux5GoxiX8T14iy1J0-QG8-U9eclJZaUxXbc-w7Zw",
    "Fruit Loops": "iOiRv66I7lmJRpWSDdFTb2ArR_XN211MT2GT_a2_UcceP0E",
    "PicklesPops": "9lupLZVWpFLXuol5qnNj5TZn1-bJlpCm05mS_qqNqmsWB6A"
}

FILENAME = "summoners.p"

def save_summoners(ids):
    outfile = open(FILENAME, "wb")
    pickle.dump(ids, outfile)
    outfile.close()

def load_summoners():
    infile = open(FILENAME, "rb")
    s = pickle.load(infile)
    infile.close()

    return s