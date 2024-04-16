import pandas as pd
from dotabet.fetch import fetch_data
from dotabet.utils import format_player_name

def check_all_values_not_nan(players_df):
    bug = False;
    
    for index, row in players_df.iterrows():
        for column in players_df.columns:
            if pd.isna(row[column]):
                print(f"❌ NaN found in column '{column}' for match_id '{row['match_id']}'"); bug=True;

    if not bug:
        print(f"all_players_clean.csv (1/1) ✅ features doesnt have any NaN")


def check_team_names_in_teams_csv_match_team_name_in_recent_features_data(teams_df, features_df):

    overall_consistency = True
    for _, row in teams_df.iterrows():
        team_id = row['Team ID']
        team_name = row['Team Name']
    
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


####################################### PLAYERS CSV ###############

def check_players_id_in_teams_csv_match_recent_features_data(teams_df, features_df):
    
    overall_consistency = True
    for team_id in teams_df['Team ID']:
        
        # Find the team row in teams_df
        team_row = teams_df[teams_df['Team ID'] == team_id]
        if team_row.empty:
            print(f"⚠️Team ID {team_id} not found in teams.csv")
            overall_consistency = False
            continue
        
        # Extract player IDs from the team_row
        team_player_ids = team_row[['Pos1ID', 'Pos2ID', 'Pos3ID', 'Pos4ID', 'Pos5ID']].values.flatten().tolist()
        
        # Filter the first 5 players from features_df for the current team
        first_5_players_df = features_df[features_df['player_team_id'] == team_id].head(5)
    
        mismatch_flag = False
        mismatch_player_ids = []
        
        # player from first 5 rows of matches
        for _, player in first_5_players_df.iterrows(): 
            player_id = player['account_id']
            if player_id in team_player_ids:
                team_player_ids.remove(player_id)
            else:
                mismatch_player_ids.append(player_id)
                mismatch_flag = True
            
        if mismatch_flag:
            print(f"❌Mismatch found for Team ID {team_id}:")
            print(f"In CSV remaining players IDs are {team_player_ids}")
            print(f"But in features df there are {mismatch_player_ids} which is not in CSV")
            overall_consistency = False
            
    if overall_consistency:
        print(f"teams.csv(2/3).✅Team compositions from teams.csv is consistent with featuers.csv:")

def check_teams_csv_with_current_open_dota_api(teams_df):
    fetched_null = []
    wrong_names = []
    bug = False
    for team_id in teams_df['Team ID']:
        team_row = teams_df[teams_df['Team ID'] == team_id]
        for i in range(1,6):
            account_id = team_row[f'Pos{i}ID'].values[0]
            player_endpoint = f"https://opendota.com/api/players/{account_id}"
            fetched_data = fetch_data(player_endpoint)
            if not fetched_data['rank_tier'] >= 80:
                print(f"❌ In teams.csv {account_id=} has rank<80"); bug=True;

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
        print(f"⚠️ Wrong names in teams.csv and OpenDota API: {wrong_names}")
    else:
        print(f"teams.csv(3/3)✅ is up to date with opendota.com/api/players/account_id")
    

def check_all_matches_has_exactly_10_rows(df):
    filtered_matches = df.groupby('match_id').filter(lambda x: len(x) < 10)

    corrupted_match_ids = filtered_matches['match_id'].unique()
    if corrupted_match_ids:
        print("❌ Match IDs with less than 10 rows:", corrupted_match_ids)
    else:
        print(f"all_players.csv (1/1).✅ All matches has exactly 10 rows")

def check_missing_data(features_df):
    if features_df['missing_data'].any():
        print("❌ features.csv contains missing data")
    else:
        print(f"features.csv (1/3).✅No missing data")

def check_unique_composition(features_df):
    df = features_df
    bug = False
    for compos_id in df['team_composition_id'].unique():
        sliced_df = df[df['team_composition_id'] == compos_id]
        unique_accounts = sliced_df['account_id'].nunique()
        if not (unique_accounts == 5):
            print(f"❌ {sliced_df['player_team_name']} with {compos_id=} has {unique_accounts=}"); bug=True;
    if not bug:
        print(f"features.csv (2/3)✅For each composition team, all matches has only 5 different accounts")

#### 
# In file: consistency_checks.py

def check_5rows_consistency(features_df, only10rows:bool):
    """
    1. each match (match_id) has exactly 10 rows
    2. each match has exacly 2 different player_team_id
    3. each player_team_id within match, has exactly 5 rows (5 players)
    4. these 5 rows has exactly 5 different account_id
    """
    df = features_df
    bug = False
    
    for match_id, match_data in df.groupby('match_id'):
        team_ids = match_data['player_team_id'].unique()
        
        if only10rows:
            if len(match_data) != 10:
                print(f"❌Match ID {match_id} does not have exactly 10 players."); bug=True;
            if set(match_data['win'].unique()) != {0, 1}:
                print(f"❌match ID {match_id} all teams loose or win ('win' is 0 or 1 for both teams)"); bug=True;
            if len(team_ids) != 2:
                print(f"❌Match ID {match_id} does not have exactly 2 teams."); bug=True;
        
        for team_id in team_ids:
            team_data = match_data[match_data['player_team_id'] == team_id]
            if len(team_data) != 5:
                print(f"❌Team ID {team_id} in match ID {match_id} does not have exactly 5 players."); bug=True;
            if len(team_data['account_id'].unique()) != 5:
                print(f"❌Team ID {team_id} in match ID {match_id} has duplicate account IDs."); bug=True;
            if len(team_data['win'].unique()) != 1:
                print(f"❌Team ID {team_id} in match ID {match_id} has 0 and 1 'win' values"); bug=True;
            # if set(team_data['player_position']) != set([1,2,3,4,5]):
            #     print(f"❌Team ID {team_id} in match ID {match_id} doesnt have 12345 positions"); bug=True;
    if not bug:            
        print(f"features.csv (3/3)✅ has passed 10rows-consistency") 

def check_team_csv_consistency(teams_csv_path, features_csv_path):
    features_df = pd.read_csv(features_csv_path)
    teams_df = pd.read_csv(teams_csv_path)
    
    check_teams_csv_with_current_open_dota_api(teams_df)
    check_players_id_in_teams_csv_match_recent_features_data(teams_df, features_df)
    check_team_names_in_teams_csv_match_team_name_in_recent_features_data(teams_df, features_df)

def check_all_player_csv_consistency(all_player_csv_path):
    raw_players_df = pd.read_csv(all_player_csv_path)
    check_all_matches_has_exactly_10_rows(raw_players_df)

def check_all_player_clean_csv_consistency(all_player_clean_csv_path):
    players_df = pd.read_csv(all_player_clean_csv_path)
    check_all_values_not_nan(players_df)

def check_features_consistency(features_csv_path, only10rows=True):
    features_df = pd.read_csv(features_csv_path)

    check_missing_data(features_df)
    check_unique_composition(features_df)
    check_5rows_consistency(features_df, only10rows)



    