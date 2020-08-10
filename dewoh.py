import datetime
import requests
import pickle
import queues
import time
import sys
import os

import summoners

# KEY = os.environ["RIOT_API_KEY"]
print(os.environ)
exit(0)
DELAY = 0.6

SUMMONER_IDS = summoners.load_summoners()

def intersection(list_1, list_2):
    return [x for x in list_1 if x in list_2]

def get_summoner_id(summoner_name):
    if summoner_name in SUMMONER_IDS:
        print("FOUND ", summoner_name, "IN DATABASE")
        return SUMMONER_IDS[summoner_name]

    print("CALLING API TO LOOK for:", summoner_name)

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
    print("Getting match history")
    response = requests.get(f"https://oc1.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}?endIndex={end_index}&beginIndex={begin_index}&api_key={KEY}")
    time.sleep(DELAY)

    if not response.ok:
        if response.status_code == 504:
            print(f"ERROR get_match_history: status code {response.status_code}. Retrying...")
            return get_match_history(account_id, begin_index, end_index)

        print(f"ERROR get_match_history: status code {response.status_code}")
        exit(1)

    return response.json()

def get_game_ids(account_id, pages):
    # Returns a list of game ids that they have played in

    game_ids = []
    max_index = pages * 100
    for begin_index in range(0, max_index, 100):
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
    time.sleep(DELAY)

    if not response.ok:
        if response.status_code == 504:
            print(f"ERROR get_game_information: status code {response.status_code}. Retrying...")
            return get_game_information(game_id, a1, a2)

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
        return (-1, game_data["gameCreation"], -1)

    # find the team outcome WIN/LOSE
    for t in game_data["teams"]:
        if t["teamId"] == teamId:
            return (t["win"] == "Win", game_data["gameCreation"], game_data["queueId"])

def determine_game_outcomes(common_game_ids, sum_1_id, sum_2_id):
    wins, losses, game_timestamp = (0, 0, 0)

    game_results = {"W": 0, "L": 0}

    index = 1
    for g in common_game_ids:
        time.sleep(DELAY)
        result, game_timestamp, queue_id = get_game_information(g, sum_1_id, sum_2_id)

        if result == -1:
            print(index, "/", len(common_game_ids), "checking game_id: ", g, "n/a - played as opponents", time.ctime(game_timestamp/1000))
            index += 1
            continue
        
        if queue_id not in game_results:
            game_results[queue_id] = {"W": 0, "L": 0}
        
        if result == 1:
            print(index, "/", len(common_game_ids), "checking game_id: ", g, "win", time.ctime(game_timestamp / 1000))
            game_results[queue_id]["W"] += 1
            game_results["W"] += 1
        else:
            print(index, "/", len(common_game_ids), "checking game_id: ", g, "loss", time.ctime(game_timestamp / 1000))
            game_results[queue_id]["L"] += 1
            game_results["L"] += 1
        index += 1
    
    return (game_results, game_timestamp / 1000)

def print_dewoh(game_results, sum_name_1, sum_name_2, game_timestamp):

    overall_wins = game_results["W"]
    overall_losses = game_results["L"]
    overall_games = overall_wins + overall_losses
    
    if overall_games == 0:
        print(f"\n{sum_name_1} and {sum_name_2} have not played together recently")
        return

    overall_win_rate = 100.0 * overall_wins / overall_games


    print(f"\nWIN RATE STATISTICS FOR {sum_name_1} AND {sum_name_2}")
    print("-------------------------------------------------------")
    print(f"Overall: {overall_wins} / {overall_games} won: {overall_win_rate}% since ", time.ctime(game_timestamp))
    print("-------------------------------------------------------")
    print("Breakdown by queue:")

    for q in game_results:
        if q == "W" or q == "L":
            continue

        q_data = queues.find_queue(q)
        q_desc = q_data["description"]

        q_wins = game_results[q]["W"]
        q_losses = game_results[q]["L"]
        q_games = q_wins + q_losses
        q_win_rate = 100.0 * q_wins / q_games

        print(f"{q_desc} - {q_wins} / {q_games} won: {q_win_rate}%")

################################################################################
#                                                                              #
#                                   MAIN                                       #
#                                                                              #
################################################################################

if len(sys.argv) != 4:
    print("USAGE: python3 dewoh.py <SUMMONER_NAME_1> <SUMMONER_NAME_2> <pages>")
    exit(1)

sum_name_1 = sys.argv[1]
sum_name_2 = sys.argv[2]
pages = int(sys.argv[3])

sum_1_id = get_summoner_id(sum_name_1)
sum_2_id = get_summoner_id(sum_name_2)

sum_1_game_ids = get_game_ids(sum_1_id, pages)
sum_2_game_ids = get_game_ids(sum_2_id, pages)

common_game_ids = intersection(sum_1_game_ids, sum_2_game_ids)
print("Common games:", common_game_ids)

game_results, game_timestamp = determine_game_outcomes(common_game_ids, sum_1_id, sum_2_id)

print_dewoh(game_results, sum_name_1, sum_name_2, game_timestamp)
    
