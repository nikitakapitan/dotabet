import csv 
import dotabet
import json

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
            'radiant_player_ids': radiant_player_ids,
            'dire_player_ids': dire_player_ids,
            'radiant_win': match['radiant_win'],
            'dire_team_id' : match['dire_team_id'],
            'radiant_team_id' : match['radiant_team_id'],
        }
        rows.append(row)
    
    # Write to CSV
    with open(dotabet.train_path, 'w', newline='') as csvfile:
        fieldnames = [ 'start_time', 'radiant_player_ids', 'dire_player_ids', 'radiant_win', 'dire_team_id', 'radiant_team_id']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in rows:
            writer.writerow(row)