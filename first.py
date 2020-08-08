import summoners
import champions
import requests
import queues
import time
import sys


KEY = "RGAPI-8311e81c-3fca-4487-a41f-da2cee2314aa"
SUMMONER_IDS = summoners.load_summoners()
DELAY = 0.6


def get_summoner_id(summoner_name):
    if summoner_name in SUMMONER_IDS:
        print("FOUND ", summoner_name, "IN DATABASE")
        return SUMMONER_IDS[summoner_name]

    print("CALLING API TO LOOK for ", summoner_name)

    response = requests.get(f"https://oc1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={KEY}")
    time.sleep(DELAY)

    if not response.ok:
        if response.status_code == 504:
            print(f"ERROR get_summoner_id: status code {response.status_code}. Retrying...")
            return get_summoner_id(summoner_name)

        print(f"ERROR get_summoner_id: status code {response.status_code}")
        exit(1)

    account_id = response.json()["accountId"]
    print("Account ID for", summoner_name, "is", account_id)
    print("Saving to database...")

    SUMMONER_IDS[summoner_name] = account_id
    summoners.save_summoners(SUMMONER_IDS)

    return account_id

def get_match_history(account_id, begin_index, end_index):
    print("Getting match history from", begin_index, "to", end_index)
    response = requests.get(f"https://oc1.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}?endIndex={end_index}&beginIndex={begin_index}&api_key={KEY}")
    time.sleep(DELAY)

    if not response.ok:
        if response.status_code == 504:
            print(f"ERROR get_match_history: status code {response.status_code}. Retrying...")
            return get_match_history(account_id, begin_index, end_index)

        # ASSUME WHATEVER RESPNSE CODE HERE IS END OF THIGN
        print(f"ERROR get_match_history: status code {response.status_code}")
        return {"not_found": "found"}

    return response.json()

if len(sys.argv) != 2:
    print("USAGE: python3 first.py <SUMMONER_NAME_1>")
    exit(1)



sum_name = sys.argv[1]

sum_id = get_summoner_id(sum_name)

# FIND FIRST 10
prev_match_history = {}
curr_match_history = {}
index = 1200
matches_found = 1

while 1:
    curr_match_history = get_match_history(sum_id, index, index + 100)

    # print(curr_match_history)

    if not curr_match_history["matches"]:
        break

    prev_match_history = curr_match_history

    index += 100

counter = 1
for g in prev_match_history["matches"]:
    c = champions.find_champion(g["champion"])
    q = queues.find_queue(g["queue"])
    game_timestamp = g["timestamp"] / 1000 # millisceonds

    print("c =", c)

    c_name = c["id"]
    q_desc = q["description"]
    
    print("GAME", counter, ":", c_name, q_desc, time.ctime(game_timestamp))

    counter += 1

# print(prev_match_history)

