import json
import yaml
import dotabet
from dotabet.fetch import fetch_data
import datetime

single_match_endpoint = 'https://api.opendota.com/api/matches/{}'
meta_file = '../data/1pro_games_meta.yaml'  # Metadata file path

keys2keep = "dire_captain dire_name dire_team_id game_mode leagueid start_time\
 lobby_type metadata patch picks_bans players radiant_captain radiant_gold_adv\
 radiant_name radiant_score radiant_team_id radiant_win radiant_xp_adv\
 tower_status_dire tower_status_radiant version".split()

players_keys2keep = "account_id actions_per_min ancient_kills assists\
 benchmarks buyback_count camps_stacked cluster creeps_stacked deaths denies\
 firstblood_claimed gold_per_min gold_t hero_damage hero_healing hero_id hero_kills\
 kda kill_streaks kills kills_per_min lane lane_efficiency lane_efficiency_pct\
 lane_kills lane_role last_hits lh_t life_state_dead lose multi_kills net_worth\
 neutral_kills observers_placed observer_kills patch pings radiant_win rank_tier\
 roshan_kills rune_pickups sentry_kills sen_placed teamfight_participation\
 total_gold total_xp tower_damage tower_kills win xp_per_min xp_t".split()

def get_filtered_data(fetched_data, match_id):
    filtered_data = {'match_id' : match_id}
    for key in keys2keep:
        if key == 'players':
            filtered_data['players'] = []
            for player_dict in fetched_data['players']:
                filtered_player = {key: player_dict[key] for key in players_keys2keep if key in player_dict}
                filtered_data['players'].append(filtered_player)
        else:
            filtered_data[key] = fetched_data.get(key, None)
    return filtered_data

def get_new_matches():
    telegram_msg = []
    output_file = r"D:\WORKSPACE\dotabet\data\1pro_games_tmp.json"
    data = dotabet.utils.load_tmp_file(output_file)
    data_mids = [m['match_id'] for m in data]

    start_match_id = None # the most recent
    stop_match_id = max(data_mids) # the newest available
    recent_start_time = data[data_mids.index(stop_match_id)]['start_time']
    recent_date = datetime.datetime.utcfromtimestamp(recent_start_time)
    telegram_msg += [f"Most recent avaialble match={stop_match_id} [{recent_date.strftime('%d %B %Y %H:%M')}]\n"]
    print(f"Ready to fetch the Newest. Most recent id: {stop_match_id} ({recent_date.strftime('%d %B %Y %H:%M')})")

    endpoint_proMatches = "https://api.opendota.com/api/proMatches"

    stop = False
    while 1: # loop over API batches of 100 before stop_match_id is reached.
        fetched_proMatches = fetch_data(endpoint_proMatches)
        fetched_mids = [m['match_id'] for m in fetched_proMatches]
        for i,match_id in enumerate(fetched_mids):
            if match_id in data_mids:
                continue
            if match_id <= stop_match_id:
                stop = True
                print(f"Finish 🏁 Reached {match_id=}")
                break
                
            endpoint = single_match_endpoint.format(match_id)
            fetched_data = fetch_data(endpoint)
            if fetched_data:
                filtered_data = get_filtered_data(fetched_data, match_id)
                with open(output_file, 'a') as file:
                    json.dump(filtered_data, file)
                    file.write(',') 
                print(f"[{i}] {match_id=}✔️", end='')  
            else:
                print("No new data fetched. Ending loop.")
                break
        if stop:
            break
        endpoint_proMatches = f"https://api.opendota.com/api/proMatches?less_than_match_id={match_id}"
        print("Next 💯", end=' ')

    with open(output_file, 'r', encoding='utf-8') as file:
            tmp_data = file.read()
            tmp_data = '[' + tmp_data[:-1] + ']'
            tmp_data = json.loads(tmp_data)

    if len(tmp_data) >= 100:
        file_to_merge = r"D:\WORKSPACE\dotabet\data\1pro_games_2.json"
        telegram_msg += dotabet.utils.merge_fetched_data(output_file, file_to_merge)
    else:
        telegram_msg += [f"Get new up to match={match_id}\n Didnt merge: total nb tmp matches : {len(tmp_data)}<100"]
        
    print("".join(telegram_msg))
    return telegram_msg