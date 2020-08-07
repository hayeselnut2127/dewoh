import sys
import time
import pickle
import requests
import datetime

import summoners

KEY = "RGAPI-41b0f0c2-eeff-483c-9195-76d8fe0d604d"

SUMMONER_IDS = summoners.load_summoners()

def intersection(list_1, list_2):
    return [x for x in list_1 if x in list_2]

def get_summoner_id(summoner_name):
    if summoner_name in SUMMONER_IDS:
        print("FOUND ", summoner_name, "IN DATABASE")
        return SUMMONER_IDS[summoner_name]

    print("CALLING API TO LOOK for ", summoner_name)

    response = requests.get(f"https://oc1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={KEY}")

    if not response.ok:
        print(f"ERROR get_summoner_id: status code {response.status_code}")
        exit(1)

    account_id = response.json()["accountId"]
    print("Account ID for", summoner_name, "is", account_id)
    print("Saving to database...")

    SUMMONER_IDS[summoner_name] = account_id
    summoners.save_summoners(SUMMONER_IDS)

    return account_id

def get_match_history(account_id, begin_index, end_index):
    print("Getting match history")
    response = requests.get(f"https://oc1.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}?endIndex={end_index}&beginIndex={begin_index}&api_key={KEY}")

    if not response.ok:
        print(f"ERROR get_match_history: status code {response.status_code}")
        exit(1)

    return response.json()

def get_game_ids(account_id, pages):
    # Returns a list of game ids that they have played in

    game_ids = []
    max_index = pages * 100
    for begin_index in range(0, pages, 100):
        match_history = get_match_history(account_id, begin_index, begin_index + 100)

        for match in match_history["matches"]:
            game_ids.append(match["gameId"])

    return game_ids

def get_participant_id(game_data, id):
    for p in game_data["participantIdentities"]:
        # print(p["player"]["currentAccountId"], p["player"]["summonerName"])
        if p["player"]["currentAccountId"] == id:
            return p["participantId"]

    print("ERROR get_participant_id: id not found for", id)
    exit(1)

def verify_same_team(game_data, part_id1, part_id2):
    team1 = game_data["participants"][part_id1 - 1]["teamId"]
    team2 = game_data["participants"][part_id2 - 1]["teamId"]

    if team1 == team2:
        return team1

    return 0

def get_game_information(game_id, a1, a2):
    response = requests.get(f"https://oc1.api.riotgames.com//lol/match/v4/matches/{game_id}?api_key={KEY}")

    if not response.ok:
        print(f"ERROR get_game_information: status code {response.status_code}")
        exit(1)

    game_data = response.json()

    part_id1 = get_participant_id(game_data, a1)
    part_id2 = get_participant_id(game_data, a2)

    # Use game_data["participantIdentities"] towork who paticipant identity

    # Verify they are on the same team
    # if not same team --> skip this match
    teamId = verify_same_team(game_data, part_id1, part_id2)

    if teamId == 0:
        return (-1, 0)

    # find the team outcome WIN/LOSE
    for t in game_data["teams"]:
        if t["teamId"] == teamId:
            return (t["win"] == "Win", game_data["gameCreation"])


################################################################################
#                                                                              #
#                                   MAIN                                       #
#                                                                              #
################################################################################

# SUM_1 = "Hayeselnut" # input("First summoner name: ")
# SUM_2 = "eZED" # input("Second summoner name: ")

if len(sys.argv) != 4:
    print("USAGE: python3 dewoh.py SUMMONER_NAME_1 SUMMONER_NAME_2")
    exit(1)


sum_name_1 = sys.argv[2]
sum_name_2 = sys.argv[3]

sum_1_id = get_summoner_id(sum_name_1)
sum_2_id = get_summoner_id(sum_name_2)

sum_1_game_ids = get_game_ids(sum_1_id, 2)
sum_2_game_ids = get_game_ids(sum_2_id, 2)

common_game_ids = intersection(sum_1_game_ids, sum_2_game_ids)

print("Common games:", common_game_ids)

wins = 0
losses = 0
game_timestamp = 0

index = 1
games_to_check = len(common_game_ids)
for g in common_game_ids:
    print(index, "/", games_to_check, "checking game_id: ", g)
    index += 1
    time.sleep(1)
    (game_result, game_timestamp) = get_game_information(g, sum_1_id, sum_2_id)

    if game_result == -1:
        continue
    elif game_result == 1:
        wins += 1
    else:
        losses += 1

total_games = wins + losses

win_rate = 100.0 * wins / total_games

print ("")
print ("Win rate between", sum_name_1, "and", sum_name_2)
print(f"{wins} / {total_games} won: {win_rate}% since ", time.ctime(game_timestamp), game_timestamp)