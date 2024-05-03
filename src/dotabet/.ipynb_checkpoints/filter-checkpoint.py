import json
import csv
import dotabet
import pandas as pd
import os

# Function to filter JSON file based on team IDs and write to new JSON file
def filter_json(input_json_paths, team_ids):
    filtered_data = []
    data = dotabet.utils.get_merged_data(input_json_paths)
    for entry in data:
        if entry['dire_team_id'] in team_ids or entry['radiant_team_id'] in team_ids:
            filtered_data.append(entry)
    return filtered_data

def filter_top_teams(input_json_paths, teams_csv_path, output_file):
    team_ids = dotabet.utils.get_teams_ids(teams_csv_path)
    filtered_data = filter_json(input_json_paths, team_ids)
    print(f"Total of {len(filtered_data)} pro games")
    
    with open(output_file, 'w') as jsonfile:
        json.dump(filtered_data, jsonfile)


def filter_cur_team_composition(data_csv_path, teams_csv_path):

    data_df = pd.read_csv(data_csv_path)
    const_teams_df = pd.read_csv(teams_csv_path)

    cur_teams_features = data_df[data_df['team_composition_id'].isin(const_teams_df['team_composition_id'].values)]
    directory_name, file_name = os.path.split(data_csv_path)
    cur_teams_features.to_csv(os.path.join(directory_name, os.path.splitext(file_name)[0] + '_cur_teams.csv'))




    