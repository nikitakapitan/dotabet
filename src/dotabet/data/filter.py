import json
import csv
import dotabet
import pandas as pd
import os

# Function to filter JSON file based on team IDs and write to new JSON file
def filter_json(input_json_paths, team_ids):
    data = dotabet.utils.get_merged_data(input_json_paths)
    init_len = len(data)
    
    filtered_data = []
    for entry in data:
        try:
            dire_team_id, radiant_team_id = int(str(entry['dire_team_id'])), int(str(entry['radiant_team_id']))
        except ValueError as e:
            continue

        if dire_team_id in team_ids and radiant_team_id in team_ids:
            filtered_data.append(entry)
                
    print(f">>>filter.py: After top-teams filter, we got from {init_len} -> {len(filtered_data)} matches filtered")
    return filtered_data

def filter_top_teams(input_json_paths, teams_csv_path, output_file):
    team_ids = dotabet.utils.get_teams_ids(teams_csv_path)
    filtered_data = filter_json(input_json_paths, team_ids)
    
    with open(output_file, 'w') as jsonfile:
        json.dump(filtered_data, jsonfile)






    