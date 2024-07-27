from dotabet.fetch import fetch_data
from dotabet.utils import format_player_name
import pandas as pd
import dotabet

def _check_team_names_in_teams_csv_match_team_name_in_recent_features_data(teams_df, features_df, logs):
    """
    teams_df : df from "D:\WORKSPACE\dotabet\constants\teams.csv"
    >>> Loop over rows in teams_df
    1. check if team_id (teams_df) exists in features_df
    2. check if team_name (teams_df) matches team_name (features_df)
    """

    overall_consistency = True
    for _, row in teams_df.iterrows():
        team_id = row['team_id']
        team_name = row['team_name']
    
        # Find the first row in features_df.csv with the matching team ID
        match_row = features_df[features_df['player_team_id'] == team_id].head(1)
        
        # If no match found in features_df.csv
        if match_row.empty:
            print(f"⚠️Team ID {team_id} from teams.csv is not found in matches")
            overall_consistency = False
            continue
        
        # Check for name consistency
        if match_row.iloc[0]['player_team_name'] != team_name:
            team_name_in_matches = match_row.iloc[0]['player_team_name']
            print(f"❌Mismatch found for Team ID {team_id}:")
            print(f"CSV {team_name=}  but {team_name_in_matches=}")
            overall_consistency = False
            
    if overall_consistency:
        print(f"teams.csv(1/3)✅Team Names from teams.csv is consistent with features.csv")    


def check_team_composition_id_team_csv_against_api(teams_df, logs=False):
    
    overall_consistency = True
    for idx, team_id in enumerate(teams_df['team_id']):
        team_name = dotabet.utils.get_team_name(team_id)
        
        team_row = teams_df[teams_df['team_id'] == team_id]
        csv_current_player_ids = team_row[['Pos1ID', 'Pos2ID', 'Pos3ID', 'Pos4ID', 'Pos5ID']].values.flatten().tolist()
        
        data = dotabet.fetch.fetch_data(f"https://api.opendota.com/api/teams/{team_id}/players")
        api_current_players = [player for player in data if player['is_current_team_member']]
        api_current_players_ids = [player['account_id'] for player in api_current_players]

        all_present = all(player_id in api_current_players_ids for player_id in csv_current_player_ids)
        reserve_players = [f"{player['name']}({player['account_id']})" for player in api_current_players if player['account_id'] not in csv_current_player_ids]

        
        if logs and all_present:
            print(f"{idx}✔️{team_id=}({team_name})  all CSV players are current members. {reserve_players=}")
        if not all_present:
            if logs and len(api_current_players_ids)<5:
                print(f"{idx}⚠️🖖{team_id=}({team_name})  API doesnt have 5 active players")
            if len(api_current_players_ids)>=5:
                missing_players = [player_id for player_id in csv_current_player_ids if player_id not in api_current_players_ids]
                print(f"❌ {team_id=}({team_name})  Players in CSV but not in API: {missing_players}")
                api_players = [f"{player['name']}({player['account_id']})" for player in api_current_players]
                print(f"\t Players from API: {api_players}")
                overall_consistency = False
            
            
    if overall_consistency:
        print(f"teams.csv(2/3).✅Team compositions from teams.csv is consistent with featuers.csv:")

def _check_teams_csv_posID_and_name_against_open_dota_api(teams_df, logs):
    """
    Loop over teams & player_id in CSV
    1. check if player_rank >= 80
    2. check if csv_name == api_name
    """
    fetched_null = []
    wrong_names = []
    bug = False
    for team_id in teams_df['team_id']:
        team_row = teams_df[teams_df['team_id'] == team_id]
        for i in range(1,6):
            account_id = team_row[f'Pos{i}ID'].values[0]
            player_endpoint = f"https://opendota.com/api/players/{account_id}"
            fetched_data = fetch_data(player_endpoint)
            if not fetched_data['rank_tier'] >= 80:
                print(f"❌ In teams.csv {account_id=} has rank<80"); 
                continue
            csv_name = format_player_name(team_row[f'Pos{i}'].values[0])

            fetched_name, fetched_personaname = None, None
            if fetched_data['profile']['name']:
                fetched_name = format_player_name(fetched_data['profile']['name'])
            if fetched_data['profile']['personaname']:
                fetched_personaname = format_player_name(fetched_data['profile']['personaname'])
                
            if not fetched_name and not fetched_personaname:
                fetched_null.append((csv_name, account_id))
            elif csv_name not in [fetched_name, fetched_personaname]:
                bug = True
                wrong_names.append((csv_name, fetched_data['profile']['name'], fetched_data['profile']['personaname']))
            else:
                pass
    if fetched_null:
        print(f"⚠️ Fetched 'null' names for {fetched_null}")
    if bug:
        print(f"❌ Wrong names in teams.csv and OpenDota API (csv_name, api_profile_name, api_profile_personaname: {wrong_names}")
    else:
        print(f"teams.csv(3/3)✅ is up to date with opendota.com/api/players/account_id")
    