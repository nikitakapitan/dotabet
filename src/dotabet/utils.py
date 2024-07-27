import yaml
import os
import requests
import json
import csv
import shutil
import dotabet

class PlayerRankLess80Error(Exception):
    """Exception raised for invalid player names."""

    def __init__(self, name, message="Player Rank is Less than 80"):
        self.name = name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.name} : {self.message}'

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

############### TEAMS ##############
teams_path = r"D:\WORKSPACE\dotabet\constants\teams.csv"

def get_team_name(id):
    response = requests.get(f"https://api.opendota.com/api/teams/{id}")
    if response.status_code == 200:
        data = response.json()
        
        if data['name']:
            return data['name']
        elif data['tag']:
            return data['tag']        
    return None

def get_team_id(name):
    with open(teams_path, "r", newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if format_team_name(row['team_name']) == format_team_name(name):
                return row['team_id']
    return None

def get_team_rating(name):
    team_id = get_team_id(name)
    if team_id:
        endpoint = f"https://www.opendota.com/api/teams/{team_id}"
        rating = dotabet.fetch.fetch_data(endpoint)['rating']
        return rating



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
            
            if not data['rank_tier']:
                print(f"⚠️ {player_id=} has no rank")
            elif data['rank_tier'] < 80:
                raise PlayerRankLess80Error(data['profile']['personaname'], f"❌ {player_id=} rank less than 80 : rank={data['rank_tier']}") 
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


import re

def format_player_name(name):
    # Cast player name Avatar1k\u963F\u53D1!@# -> avatar1k
    formatted_name = re.sub(r'[^a-z1-9]', '', name.lower())  # Lowercase and remove unwanted symbols
    return formatted_name

from datetime import datetime
def cast_seconds_to_datetime(seconds):
    return datetime.utcfromtimestamp(seconds).date()
def cast_seconds_to_ymd(seconds):
    return datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d')
def cast_ymd_to_datetime(ymd_str):
    return datetime.strptime(ymd_str, '%Y-%m-%d')
def cast_datetime_to_ymd(dt):
    return dt.strftime('%Y-%m-%d')

def format_team_name(name):
    dct = {"g2.ig" : "g2 x ig",
          "bb" : "betboom",}
    if not name:
        return None
    name = name.lower()
    for w in ['team', 'esports', '1xbet', 'ray', 'gaming', ]:
        name = name.replace(w, '')
    name = name.replace('.', ' ')
    name = name.strip()
    if name in dct:
        return dct[name]
    return name




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
            if os.path.isfile(file_path) and (filename.endswith('.json') or filename.endswith('.csv')):
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

def get_teams_ids(teams_csv_path, top_teams=False, return_as_dict_with_top=False):
    team_ids = set()
    team_ids_top = {}
    with open(teams_csv_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if top_teams and not row['top']=='1':
                continue
            team_id = int(row['team_id'])
            team_ids.add(team_id)
            team_ids_top[team_id] = bool(int(row['top']))

    return team_ids_top if return_as_dict_with_top else team_ids

def get_teams_composition_ids(teams_csv_path, top=False):
    team_ids = set()
    with open(teams_csv_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['team_composition_id']: # avoid int('') error
                if top and not row['top']=='1':
                    continue
                team_ids.add(int(row['team_composition_id']))
    return team_ids

def get_team_composition_id(team_id):
    with open(teams_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if int(row['team_id']) == team_id: 
                if row['team_composition_id']: # avoid int('') error
                    return int(row['team_composition_id'])

def get_account_ids(accounts_csv_path):
    account_ids = set()
    with open(accounts_csv_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # Define the columns to extract the IDs from
        id_columns = ['Pos1ID', 'Pos2ID', 'Pos3ID', 'Pos4ID', 'Pos5ID']
        for row in reader:
            # Loop through each specified column and add the ID to the set
            for column in id_columns:
                if row[column]:  # Check if the column is not empty
                    account_ids.add(int(row[column]))
    return account_ids

# MERGE (without very last match, to keep tmp file non-empty)

def merge_fetched_data(tmp_file, file_to_merge):
    message = []

    # file_to_merge = r"D:\WORKSPACE\dotabet\data\1pro_games_2.json"
    # tmp_file = r"D:\WORKSPACE\dotabet\data\1pro_games_tmp.json"
    
    directory = os.path.dirname(file_to_merge)
    backup_file = os.path.join(directory, 'backup_' + os.path.basename(file_to_merge))
    shutil.copyfile(file_to_merge, backup_file)
    
    with open(file_to_merge, 'r', encoding='utf-8') as file:
            data1 = json.load(file)
        
    mids1 = {m['match_id'] for m in data1}
    
    with open(tmp_file, 'r', encoding='utf-8') as file:
            data_tmp = file.read()
            data_tmp = '[' + data_tmp[:-1] + ']'
            data_tmp = json.loads(data_tmp)

    filtered_data_tmp = []
    for match_tmp in data_tmp:
        if match_tmp['match_id'] in mids1:
            print(f"❌ Match {match_tmp['match_id']} from {tmp_file} is already present in {file_to_merge}")
        else:
            filtered_data_tmp.append(match_tmp)

    assert filtered_data_tmp[0]['match_id'] not in mids1, "For some reasons, the buffer tmp match was previously merged into files"
    with open(file_to_merge, 'w') as file:
        json.dump(data1 + [filtered_data_tmp[0]] + filtered_data_tmp[2:], file, separators=(',', ':'))
    
    json_string = json.dumps(data_tmp[1], ensure_ascii=False, separators=(',', ': '), default=lambda x: None if x is None else str(x).lower())
    with open(tmp_file, 'w') as file:
        file.write(json_string+',')
    message += [f"Merged new {len(data_tmp)-1} matches >> {os.path.basename(file_to_merge)}({len(data1)} matches). Total matches : {len(data_tmp)-1+len(data1)}\n"]
    buffer_date = datetime.utcfromtimestamp(data_tmp[1]['start_time'])
    message += [f"Latest match: tmp 1️⃣ buffer match: {data_tmp[1]['match_id']} ({buffer_date.strftime('%d %B %Y %H:%M')})"]
    return message
