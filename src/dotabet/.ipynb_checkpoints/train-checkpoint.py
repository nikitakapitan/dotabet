import csv 
import dotabet
import json
import numpy as np
import dotabet
import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

def create_train_csv_from_input_files():
    with open(dotabet.pro_games_json_path) as file:
        data = json.load(file)
        
    rows = []
    
    for match in data:
        if len(match['players']) == 2: # skip 1 vs 1
            continue
        radiant_player_ids = [player['account_id'] for player in match['players'] if player['win'] == match['radiant_win']]
        dire_player_ids = [player['account_id'] for player in match['players'] if player['win'] != match['radiant_win']]

        assert len(radiant_player_ids) == 5, f"train: {match['match_id']=}: no 5 radiant ids"
        assert len(dire_player_ids) == 5, f"train: {match['match_id']=}: no 5 dire ids"
        
        # Create a dictionary for the row
        row = {
            'start_time': match['start_time'],
            'match_id' : match['match_id'],
            'radiant_player_ids': radiant_player_ids,
            'dire_player_ids': dire_player_ids,
            'radiant_win': match['radiant_win'],
            'dire_team_id' : match['dire_team_id'],
            'radiant_team_id' : match['radiant_team_id'],
        }
        rows.append(row)
    
    # Write to CSV
    with open(dotabet.train_matches_path, 'w', newline='') as csvfile:
        fieldnames = [ 'start_time', 'match_id', 'radiant_player_ids', 'dire_player_ids', 'radiant_win', 'dire_team_id', 'radiant_team_id']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def compute_performance_diff():
    matches_df = pd.read_csv(dotabet.train_matches_path)
    features_df = pd.read_csv(dotabet.features_csv_path)
    features_df['start_time'] = pd.to_datetime(features_df['start_time'])
    
    result_data = []
    
    # Convert start_time to datetime for easy comparison
    matches_df['start_time'] = pd.to_datetime(matches_df['start_time'], unit='s')

    perf_cols = dotabet.groupby.numeric_features

    counters = {
        'no_data_count': 0,
        'no_won_count': 0,
        'no_loss_count': 0,
        'skip_count': 0
    }

    # Loop over each match
    for _, match in matches_df.iterrows():
        start_time = match['start_time']
        radiant_players = eval(match['radiant_player_ids'])
        dire_players = eval(match['dire_player_ids'])

        radiant_win_perf = []
        radiant_loss_perf = []
        dire_win_perf = []
        dire_loss_perf = []


        # Get performances for Radiant players
        for player_id in radiant_players:
            perf = dotabet.cumsum.make_player_cumsum(features_df, player_id, start_time, match_count=40)
            assert len(perf) <= 2, f"train.py: player perf has more than 2 rows (for win=0 and win=1) : {len(perf)=}"
            
            recent_win_perf = perf[perf['win'] == 1]
            recent_loss_perf = perf[perf['win'] == 0]

            if perf.empty:
                counters['no_data_count'] += 1
            elif recent_win_perf.empty:
                counters['no_won_count'] += 1
            elif recent_loss_perf.empty:
                counters['no_loss_count'] += 1
                
            radiant_win_perf.append(recent_win_perf[dotabet.groupby.numeric_features])
            radiant_loss_perf.append(recent_loss_perf[dotabet.groupby.numeric_features])

        # Get performances for Dire players
        for player_id in dire_players:
            perf = dotabet.cumsum.make_player_cumsum(features_df, player_id, start_time, match_count=40)
            assert len(perf) <= 2, f"train.py: player perf has more than 2 rows (for win=0 and win=1) : {len(perf)=}"
            
            recent_win_perf = perf[perf['win'] == 1]
            recent_loss_perf = perf[perf['win'] == 0]

            if perf.empty:
                counters['no_data_count'] += 1
            elif recent_win_perf.empty:
                counters['no_won_count'] += 1
            elif recent_loss_perf.empty:
                counters['no_loss_count'] += 1

            dire_win_perf.append(recent_win_perf[dotabet.groupby.numeric_features])
            dire_loss_perf.append(recent_loss_perf[dotabet.groupby.numeric_features])

        assert len(radiant_win_perf) == 5, f"train: not 5 players were used to fetch performance: {match['match_id']=} {len(radiant_players)=} {len(radiant_win_perf)=}"
        assert len(radiant_loss_perf) == 5, f"train: not 5 players were used to fetch performance: {match['match_id']=} {len(radiant_players)=} {len(radiant_loss_perf)=}"
        assert len(dire_win_perf) == 5, f"train: not 5 players were used to fetch performance: {match['match_id']=} {len(dire_players)=} {len(dire_win_perf)=}"
        assert len(dire_loss_perf) == 5, f"train: not 5 players were used to fetch performance: {match['match_id']=} {len(dire_players)=} {len(dire_loss_perf)=}"
        


        # skip if 2 None or more
        if sum(1 for perf in radiant_win_perf if perf.empty) > 2 or sum(1 for perf in dire_win_perf if perf.empty) > 2:
            counters['skip_count'] += 1
            continue
            
        # Calculate average performance
        radiant_win_perfs = pd.concat(radiant_win_perf, ignore_index=True)
        dire_win_perfs = pd.concat(dire_win_perf, ignore_index=True)
        win_diff = radiant_win_perfs.mean() - dire_win_perfs.mean()
        row = win_diff.to_dict()
        row['match_time'] = start_time
        row['match_id'] = match['match_id']
        row['data_win'] = True
        row['radiant_win'] = match['radiant_win']
        result_data.append(row)
        
        # skip if 2 None or more
        if sum(1 for perf in radiant_loss_perf if perf.empty) > 2 or sum(1 for perf in dire_loss_perf if perf.empty) > 2:
            counters['skip_count'] += 1
            continue
        
        radiant_loss_perfs = pd.concat(radiant_loss_perf, ignore_index=True)
        dire_loss_perfs = pd.concat(dire_loss_perf, ignore_index=True)
        loss_diff = radiant_loss_perfs.mean() - dire_loss_perfs.mean()
        row = loss_diff.to_dict()
        row['match_time'] = start_time
        row['match_id'] = match['match_id']
        row['data_win'] = False
        row['radiant_win'] = match['radiant_win']
        result_data.append(row)

    
    result_df = pd.DataFrame(result_data)
    # normalize
    info_columns = ['match_time', 'match_id', 'radiant_win', 'data_win']
    numerical_data = result_df.drop(columns=info_columns)
    user_info = result_df[['match_time', 'match_id', 'radiant_win', 'data_win']]

    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(numerical_data)
    standardized_df = pd.DataFrame(standardized_data, columns=numerical_data.columns)
    scaler_info = {
        'scaler': scaler,
        'columns': numerical_data.columns.tolist()
    }
    joblib.dump(scaler_info, dotabet.diff_scaler_path)
    
    final_df = pd.concat([user_info, standardized_df], axis=1)
    
    final_df.to_csv(dotabet.train_diff_path, index=False)
    print(counters)
    print(f"Performance difference file created: {dotabet.train_diff_path}")


