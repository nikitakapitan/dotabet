import pandas as pd
import ast
import numpy as np
import dotabet

teams_csv_path = r"D:\WORKSPACE\dotabet\constants\teams.csv"
teams_df = pd.read_csv(teams_csv_path)

def calculate_average_up2n(lst, n):
    if isinstance(lst, list):
        if n < len(lst):
            return int(lst[n]/n)
        else:
            ln = len(lst)
            return int(lst[ln-1]/ln)
    else:
        return np.nan


def process_time_series(df):
    cast_to_list = lambda x: eval(x) if isinstance(x, str) else x
    
    time_series_columns = ['gold_t', 'xp_t', 'lh_t']
    for col in time_series_columns:
        df[col] = df[col].apply(cast_to_list)

    for col in time_series_columns:
        for min in [10, 15, 20, 25, 30, 40]:
            df[f'{col[:-2]}{min}'] = df[col].apply(lambda x: calculate_average_up2n(x, min))
            
    df = df.drop(columns=time_series_columns)
    return df

def generate_team_composition_text(team_data, nb_char=4):
    try:
        # Temporarily create a copy with sorted player positions
        # Handling non-integer positions by converting them to NaN which are sorted first
        temp_team_data = team_data.copy()
        temp_team_data['player_position'] = pd.to_numeric(temp_team_data['player_position'], errors='coerce')
        sorted_team_data = temp_team_data.sort_values(by='player_position', na_position='first')
        
        # Extracting first four letters of 'player_name' and joining them with hyphens
        team_composition = '-'.join(sorted_team_data['player_name'].str[:nb_char])
    except Exception as e:
        print(f"features.py Error generating team composition: {e}")
        team_composition = ""
    return team_composition

def add_team_composition_and_matchup_info(df):
    df['account_id'] = df['account_id'].astype('int64')
    
    for match_id, match_data in df.groupby('match_id'):
        team_ids = match_data['player_team_id'].unique()
        df.loc[(df['match_id'] == match_id), 'teams_matchup_id'] = team_ids.sum()
        for team_id in team_ids:
            team_data = match_data[match_data['player_team_id'] == team_id]
            
            df.loc[(df['match_id'] == match_id) & (df['player_team_id'] == team_id), 'team_composition_id'] = team_data['account_id'].sum()
            df.loc[(df['match_id'] == match_id) & (df['player_team_id'] == team_id), 'team_composition'] = generate_team_composition_text(team_data)
    return df


def find_player_position(account_id, player_team_id):
    
    # Filter the teams dataframe for the current player's team
    team_row = teams_df[teams_df['team_id'] == player_team_id]

    # If team_row is empty, the team was not found
    if team_row.empty:
        return 404_040 # "Not found team in CSV"

    # Check each position column for the account_id
    for pos in ['Pos1ID', 'Pos2ID', 'Pos3ID', 'Pos4ID', 'Pos5ID']:
        if account_id in team_row[pos].values:
            # Return the position number (extracted from the column name)
            return int(pos[3])  # extract n from Pos{n}ID
    
    return account_id # "No Up to Date Player" # this player doesn't currently play in the team

def make_features(input_file_path, output_file_path):

    df= pd.read_csv(input_file_path)
    
    df = process_time_series(df)
    df['player_position'] = df.apply(lambda row: find_player_position(row['account_id'], row['player_team_id']), axis=1).astype(int)
    df = add_team_composition_and_matchup_info(df)
    df = df.sort_values(by='start_time', ascending=False) # sanity sort

    df.to_csv(output_file_path, index=False)
