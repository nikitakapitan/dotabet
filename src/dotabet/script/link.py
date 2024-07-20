import dotabet
import requests
import csv
import pandas as pd
from datetime import datetime

def determine_winner(row):
    if row['radiant_win']:
        return row['radiant_name']
    else:
        return row['dire_name']

def get_team_id(row, team_name_key):
    if row[team_name_key] == row['radiant_name']:
        return row['radiant_team_id']
    elif row[team_name_key] == row['dire_name']:
        return row['dire_team_id']
    return None

def get_score(api_df):
    score_count = api_df.groupby(level=['Match_Date', 'Teams'])['radiant_win'].apply(lambda x: f"{x.sum()}-{(len(x) - x.sum())}").reset_index()
    api_df = api_df.reset_index().merge(score_count, on=['Match_Date', 'Teams'])
    api_df.rename(columns={'radiant_win_x': 'radiant_win', 'radiant_win_y': 'score'}, inplace=True)
    api_df = api_df.drop_duplicates(subset=['Match_Date', 'Teams'], keep='first')
    api_df.set_index(['Match_Date', 'Teams'], inplace=True)
    return api_df

def standardize_index(index):
    date_part = index[0]
    frozenset_part = index[1]
    # Ensure all elements are strings and handle NoneType
    sorted_tuple = tuple(sorted([str(item) if item is not None else '' for item in frozenset_part]))
    return (date_part, sorted_tuple)


def link(api_pages=5):
    telegram_msg = []
    pinnacle_path = r"D:\WORKSPACE\dotabet\data\odds\pinnacle.csv"
    history_path = r"D:\WORKSPACE\dotabet\data\odds\history.csv"

    df = pd.read_csv(pinnacle_path)
    today = datetime.today().date()
    
    init_df_len = len(df)
    df['Team_1'] = df['Team_1'].apply(dotabet.utils.format_team_name)
    df['Team_2'] = df['Team_2'].apply(dotabet.utils.format_team_name)
    df['Teams'] = df.apply(lambda x: frozenset([x['Team_1'], x['Team_2']]), axis=1)
    df.set_index(['Match_Date', 'Teams'], inplace=True)
    df.index = df.index.map(standardize_index)

    endpoint_matches = "https://api.opendota.com/api/proMatches"
    completed_dfs = []
    for _ in range(api_pages):
        fetched_matches = dotabet.fetch.fetch_data(endpoint_matches)
    
        api_df = pd.DataFrame(fetched_matches)
        
        api_df['Match_Date'] = api_df['start_time'].apply(dotabet.utils.cast_seconds_to_datetime)
        api_df = api_df[api_df['Match_Date'] < today]
        api_df['Match_Date'] = api_df['Match_Date'].apply(dotabet.utils.cast_datetime_to_ymd)
        
        api_df['radiant_name'] = api_df['radiant_name'].apply(dotabet.utils.format_team_name)
        api_df['dire_name'] = api_df['dire_name'].apply(dotabet.utils.format_team_name)
        api_df['Teams'] = api_df.apply(lambda x: frozenset([x['radiant_name'], x['dire_name']]), axis=1)
        # api_df = api_df.drop_duplicates(subset=['Match_Date', 'Teams'], keep='first')
        api_df.set_index(['Match_Date', 'Teams'], inplace=True)
        api_df.index = api_df.index.map(standardize_index)
        api_df = get_score(api_df)
    
        merged_df = df.merge(api_df, how='inner', left_index=True, right_index=True)
    
        df = df.drop(merged_df.index)
    
        completed_dfs.append(merged_df)
        endpoint_matches = f"https://api.opendota.com/api/proMatches?less_than_match_id={fetched_matches[-1]['match_id']}"
    
    final = pd.concat(completed_dfs)
    final.reset_index(inplace=True)
    final['team1_team_id'] = final.apply(lambda row: get_team_id(row, 'Team_1'), axis=1)
    final['team2_team_id'] = final.apply(lambda row: get_team_id(row, 'Team_2'), axis=1)
    final['winner'] = final.apply(determine_winner, axis=1)
    final = final.drop(['Teams', 'League_Name', 'duration', 'start_time', 'radiant_team_id', 'radiant_name', 'version',\
                        'leagueid',\
                       'dire_team_id', 'dire_name', 'series_id', 'series_type', 'radiant_score', 'dire_score', 'radiant_win'],axis=1)
    final['team1_composition_id'] = final['team1_team_id'].apply(dotabet.utils.get_team_composition_id) 
    final['team2_composition_id'] = final['team2_team_id'].apply(dotabet.utils.get_team_composition_id) 
    odds = pd.read_csv(history_path)
    output = pd.concat([final, odds])
    output.to_csv(history_path, index=False)
    
    
    df.reset_index(inplace=True)
    df = df.drop('Teams',axis=1)
    df.to_csv(pinnacle_path, index=False)

    if not final.empty:
        telegram_msg += [f"🔗Total pinnacle.csv: {len(df)} = {init_df_len} - [{len(final)}]\n"]
        telegram_msg += [f"🔗Total odds.csv: {len(output)} = {len(odds)} + [{len(final)}]\n"]
        final['bet'] = final.apply(dotabet.checkout.calculate_bet, axis=1)
        final['coef'] = final.apply(dotabet.checkout.calculate_coef, axis=1)
        final['result'] = final.apply(dotabet.checkout.calculate_result, axis=1)
    for idx, row in final.iterrows():
        team1 = row['Team_1']+'(✔️)' if row['Team_1'] == row['winner'] else row['Team_1']
        team2 = row['Team_2']+'(✔️)' if row['Team_2'] == row['winner'] else row['Team_2']

        telegram_msg.append(f"🔗{row['Match_Date']} {team1}<>{team2} | elo net:[{row['result']}]\n")
    
    
    return telegram_msg