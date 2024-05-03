import yaml
import os
import requests
import json
import csv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

############### TEAMS ##############
team_mapping_file = os.path.join(PROJECT_ROOT, 'constants', "team_mapping.yaml")

def get_team_name(id):
    if not hasattr(get_team_name, "team_id2name"):
        with open(team_mapping_file, "r") as file:
            team_id2name = yaml.safe_load(file)
        team_name2id = {name: team_id for team_id, name in team_id2name.items()}
        get_team_name.team_id2name = team_id2name
        get_team_name.team_name2id = team_name2id
        
    return get_team_name.team_id2name[id]

def get_team_id(name):
    if not hasattr(get_team_name, "team_name2id"):
        with open(team_mapping_file, "r") as file:
            team_id2name = yaml.safe_load(file)
        get_team_name.team_id2name = team_id2name
        get_team_name.team_name2id = {name: team_id for team_id, name in team_id2name.items()}
        
    return get_team_name.team_name2id.get(name)


################ LEAGUES ###########
league_mapping_file = os.path.join(PROJECT_ROOT, 'constants', "league_mapping.yaml")

def get_league_name(id):
    if not hasattr(get_league_name, "league_id2name"):
        with open(league_mapping_file, "r") as file:
            league_id2name = yaml.safe_load(file)
        get_league_name.league_id2name = league_id2name
        
    try:
        return get_league_name.league_id2name[id]
    except KeyError:
        league_name = fetch_league_name(id)  
        if league_name:
            get_league_name.league_id2name[id] = league_name
            with open(league_mapping_file, 'r') as file:
                league_id2name = yaml.safe_load(file)
                league_id2name[id] = league_name
            with open(league_mapping_file, 'w') as file:
                yaml.safe_dump(league_id2name, file)
            print(f"No name found for league ID {id}. Fetching from API... {league_name=}")
            return league_name
        else:
            print(f"No name found for league ID {id} and unable to fetch from API.")
            return None


############### PLAYERS ####################
player_mapping_file = os.path.join(PROJECT_ROOT, 'constants', "player_mapping.yaml")

def get_player_name(id):
    if not hasattr(get_player_name, "player_id2name"):
        with open(player_mapping_file, "r") as file:
            player_name2id = yaml.safe_load(file)
        get_player_name.player_id2name = {player_id: name for name, player_id in player_name2id.items()}
        
    name = get_player_name.player_id2name.get(id, None)
    if name:
        return name
    else:
        player_name = fetch_player_name(id)
        if player_name:
            player_name = format_player_name(player_name)
        if not player_name or len(player_name)<=2:
            player_name = "noname" + str(id)
        get_player_name.player_id2name[id] = player_name
        with open(player_mapping_file, "r") as file:
            player_name2id = yaml.safe_load(file)
            player_name2id[player_name] = int(id)
        with open(player_mapping_file, 'w') as file:
                yaml.safe_dump(player_name2id, file)
        print(f"No name found for {id=}. 💻 API parse..⌛ {player_name=}")
        return player_name

def fetch_player_name(player_id):
    response = requests.get(f"https://api.opendota.com/api/players/{player_id}")
    if response.status_code == 200:
            data = response.json()
            if data['rank_tier'] >= 80:
                return data['profile']['personaname']

def fetch_league_name(league_id):
    response = requests.get(f"https://api.opendota.com/api/leagues/{league_id}")
    if response.status_code == 200:
            data = response.json()
            return data['name']


def get_player_id(name):
    if not hasattr(get_player_id, "player_name2id"):
        with open(player_mapping_file, "r") as file:
            player_name2id = yaml.safe_load(file)
        get_player_id.player_name2id = player_name2id

    id = get_player_id.player_name2id.get(name, '')
    if id:
        print(f"For {name=} {id=}")
        return id
    else:
        print(f"No ID found for {name=}")


###################### DATA TRANSFORM #############



def flatten_dict(d, parent_key='', sep='.'):
    keys2skip = "lose multi_kills kill_streaks patch radiant_win win benchmarks buyback_count cluster creeps_stacked firstblood_claimed \
    kills_per_min lane_efficiency_pct kills lane_kills life_state_dead rank_tier ".split()
    
    items = []
    for k, v in d.items():
        if k in keys2skip:
            continue
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            if new_key.split(sep)[-1] in ['gold_t','lh_t','xp_t', 'radiant_gold_adv', 'radiant_xp_adv']:
                items.append((new_key,v))
            else:
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        if new_key == 'picks_bans':
                            action = 'pick' if item['is_pick'] else 'ban'
                            items.append((f"team{item['team']}{sep}{action}{item['order']}", item['hero_id']))
                        else:
                            items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                    else:
                        items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

########################### DATA FORMAT ####################
import re

def format_player_name(name):
    # Cast player name Avatar1k\u963F\u53D1!@# -> avatar1k
    formatted_name = re.sub(r'[^a-z1-9]', '', name.lower())  # Lowercase and remove unwanted symbols
    return formatted_name


################### GOOGLE DRIVE ##############
# Copy to Drive
import shutil
import os


def copy_to_drive(output_file, gdrive_path):
    gdrive_dir = os.path.dirname(gdrive_path)
    if not os.path.exists(gdrive_dir):
        os.makedirs(gdrive_dir)
    
    try:
        if os.path.exists(gdrive_path):
            os.remove(gdrive_path)
        shutil.copy2(output_file, gdrive_dir)
        print(f"File copied successfully to {gdrive_dir}")
    except Exception as e:
        print(f"Error occurred: {e}")

def remove_files_only(folder_path):
    # List all files in the given folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)  
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    print(f"🗑️Files from {folder_path} was fully deleted")


####

def load_tmp_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            data = '[' + data[:-1] + ']'
            data = json.loads(data)
    return data

def get_merged_data(file_paths):
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    combined_data = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            combined_data.extend(data)
    return combined_data

def get_teams_ids(teams_csv_path):
    team_ids = set()
    with open(teams_csv_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            team_ids.add(int(row['Team ID']))
    return team_ids
