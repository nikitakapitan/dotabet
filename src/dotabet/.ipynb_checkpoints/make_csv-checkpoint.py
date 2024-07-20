import json
import csv
import os
import datetime
from pathlib import Path
import yaml
import dotabet
from dotabet.utils import PlayerRankLess80Error

default_player_values = {'account_id': None, 'actions_per_min': None, 'ancient_kills': None, 'assists': None,
                  'camps_stacked': None, 'deaths': None, 'denies': None, 'gold_per_min': None,
                  'gold_t': None, 'hero_damage': None, 'hero_healing': None, 'hero_id': None,
                  'hero_kills': None, 'kda': None, 'lane_efficiency': None, 'win': None,
                  # 'lane_role': None,  'lane': None,
                  'last_hits': None, 'lh_t': None, 'net_worth': None,
                  'neutral_kills': None, 'observer_kills': None,
                   'roshan_kills': None, 'rune_pickups': None, 'sentry_kills': None,
                  'sen_placed': None, 'teamfight_participation': None, 'total_gold': None,
                  'total_xp': None, 'tower_damage': None, 'tower_kills': None, 'xp_per_min': None,
                  'xp_t': None}

top_team_ids = []
with open(r"D:\WORKSPACE\dotabet\constants\teams.csv", 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if int(row['top']) == 1:
            top_team_ids.append(int(row['team_id']))

def append_all_players_data(players_data, match_data, all_players_csv_path):
    if len(players_data) != 10:
        return 1
    for player_data in players_data:
        # player_name player_team player_team_id match_id start_time account_id league_name
        fieldnames = ['player_name', 
                      'start_time',
                      'league_name',
                      'player_team_name',
                      'radiant_name',
                      'dire_name',
                      'match_id',
                      'leagueid',
                      'player_team_id', 
                      'radiant_team_id', 
                      'dire_team_id',     
                      ]+\
                    list(default_player_values.keys()) +\
                    [  
                     'game_mode', 
                    'missing_data',
                    'radiant_win',]

        league_name = dotabet.utils.get_league_name(match_data['leagueid'])
        try:
            player_name = dotabet.utils.get_player_name(player_data['account_id'])
        except PlayerRankLess80Error as e:
            if match_data['radiant_team_id'] in top_team_ids and match_data['dire_team_id'] in top_team_ids:
                print("make_csv.py: 🚧🚨⚠️🚨🚧" + str(e) + ".\n\t" + f"match_id={match_data['match_id']}\n\t radiant={match_data['radiant_name']}\
                 ({match_data['radiant_team_id']}) dire={match_data['dire_name']}(({match_data['dire_team_id']}))\n\t {league_name=} 🚧🚧🚧")
            else:
                print(f"Non-top player has rank <80")
            player_name = e.name
        
        row_data = {'player_name' : player_name,
                    'league_name' : league_name,
                    'radiant_win' : match_data['radiant_win'],
                    'dire_name' : match_data['dire_name'], 
                    'radiant_name' : match_data['radiant_name'],
                    'dire_team_id' : match_data['dire_team_id'], 
                    'radiant_team_id' : match_data['radiant_team_id'],
                    **{key: match_data[key] for key in ['match_id', 'game_mode', 'leagueid']}, 
                    'start_time' : datetime.datetime.utcfromtimestamp(match_data['start_time'])}
        
        missing_data = False
        for key in default_player_values.keys():
            row_data[key] = player_data.get(key, default_player_values[key])
            if row_data[key] == default_player_values[key]:  # Check if data is missing
                missing_data = True
        if player_data['win'] == match_data['radiant_win']: # player is radiant
            row_data['player_team_id'] = match_data['radiant_team_id']
            row_data['player_team_name'] = match_data['radiant_name']
        else:
            row_data['player_team_id'] = match_data['dire_team_id']
            row_data['player_team_name'] = match_data['dire_name']
        row_data['missing_data'] = 1 if missing_data else 0
        
        
        with open(all_players_csv_path, mode='a', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if csv_file.tell() == 0:
                writer.writeheader()
            writer.writerow(row_data)
    return 0

def make_csv(input_file_path, output_file_path):

    all_players_csv_path = Path(output_file_path)

    # Reset csv
    if os.path.exists(all_players_csv_path):
        all_players_csv_path.unlink()
        all_players_csv_path.touch()

    with open(input_file_path) as file:
        matches = json.load(file)

    skip = 0
    for match in matches:    
        skip+=append_all_players_data(match['players'], match, all_players_csv_path)
        
    print(f"✅csv.py: Skipped {skip} matches. Total of {len(matches)-skip} cast to CSV {output_file_path}")

