import csv 
import dotabet
import json
import numpy as np

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

import pandas as pd
import numpy as np

def compute_performance_diff(player_performance_path):
    matches_df = pd.read_csv(dotabet.train_matches_path)
    performance_df = pd.read_csv(player_performance_path)

    
    result_data = []
    
    # Convert start_time to datetime for easy comparison
    matches_df['start_time'] = pd.to_datetime(matches_df['start_time'], unit='s')
    performance_df['cumsum_from'] = pd.to_datetime(performance_df['cumsum_from'])
    performance_df['cumsum_up_to'] = pd.to_datetime(performance_df['cumsum_up_to'])

    perf_cols = [col for col in performance_df.columns if col not in ['player_name', 'account_id', 'cumsum_from', 'cumsum_up_to', 'match_count', 'win']]

    # Loop over each match
    for _, match in matches_df.iterrows():
        start_time = match['start_time']
        radiant_players = eval(match['radiant_player_ids'])
        dire_players = eval(match['dire_player_ids'])
        radiant_win = match['radiant_win']

        radiant_win_perf = []
        radiant_loss_perf = []
        dire_win_perf = []
        dire_loss_perf = []

        # Get performances for Radiant players
        for player_id in radiant_players:
            perf = performance_df[(performance_df['account_id'] == player_id) & (performance_df['cumsum_up_to'] < start_time)]
            if not perf.empty:
                recent_win_perf = perf[perf['win'] == 1].sort_values(by='cumsum_up_to').iloc[-1][perf_cols].values if not perf[perf['win'] == 1].empty else None
                recent_loss_perf = perf[perf['win'] == 0].sort_values(by='cumsum_up_to').iloc[-1][perf_cols].values if not perf[perf['win'] == 0].empty else None
                
                radiant_win_perf.append(recent_win_perf) if recent_win_perf is not None else print(f"{player_id=} has no perf before {start_time=}")
                radiant_loss_perf.append(recent_loss_perf) if recent_loss_perf is not None else print(f"{player_id=} has no perf before {start_time=}")
            else:
                print(f"{player_id=} has no performance")

        # Get performances for Dire players
        for player_id in dire_players:
            perf = performance_df[(performance_df['account_id'] == player_id) & (performance_df['cumsum_up_to'] < start_time)]
            if not perf.empty:
                recent_win_perf = perf[perf['win'] == 1].sort_values(by='cumsum_up_to').iloc[-1][perf_cols].values if not perf[perf['win'] == 1].empty else None
                recent_loss_perf = perf[perf['win'] == 0].sort_values(by='cumsum_up_to').iloc[-1][perf_cols].values if not perf[perf['win'] == 0].empty else None
                
                dire_win_perf.append(recent_win_perf) if recent_win_perf is not None else print(f"{player_id=} has no perf before {start_time=}")
                dire_loss_perf.append(recent_loss_perf) if recent_loss_perf is not None else print(f"{player_id=} has no perf before {start_time=}")
            else:
                print(f"{player_id=} has no performance")

        for lst in [radiant_win_perf, radiant_loss_perf, dire_win_perf, dire_loss_perf]:
            assert len(lst) == 5, f"train: not 5 players were used to fetch performance: {match['match_id']=} {len(lst)=} {len(radiant_players)=} {len(dire_players)=}\
            {radiant_players=} {dire_players=}"
        

        # Calculate average performance
        avg_radiant_win_perf = np.mean(radiant_win_perf)
        avg_dire_win_perf = np.mean(dire_win_perf)
        win_diff = avg_radiant_win_perf - avg_dire_win_perf
        result_data.append([win_diff, 1, radiant_win])

        avg_radiant_loss_perf = np.mean(radiant_loss_perf)
        avg_dire_loss_perf = np.mean(dire_loss_perf)
        loss_diff = avg_radiant_loss_perf - avg_dire_loss_perf
        result_data.append([loss_diff, 0, radiant_win])

    result_df = pd.DataFrame(result_data, columns=['diff', 'data_win', 'radiant_win'])
    result_df.to_csv(dotabet.train_diff_path, index=False)


