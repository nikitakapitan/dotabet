import pandas as pd
import json
import csv
from collections import defaultdict
import dotabet

def find_nan(df):
    nan_match_ids = defaultdict(list)

    for column in df.columns:
        nan_rows = df[df[column].isna()]
        for index, row in nan_rows.iterrows():
            if row['match_id'] not in nan_match_ids[column]:
                nan_match_ids[column].append(row['match_id'])

    return dict(nan_match_ids)


def find_more60_minutes_match(df):
    more60_match_ids = defaultdict(list)
    column = "more60"
    
    rows_more60 = df[df['minutes'] > 60]
    for index, row in rows_more60.iterrows():
        if row['match_id'] not in more60_match_ids[column]:
                more60_match_ids[column].append(row['match_id'])
            
    return dict(more60_match_ids)

def find_less15_minutes_match(df):
    less15_match_ids = defaultdict(list)
    column = "less15"
    
    rows_less15 = df[(df['minutes'] > 0) & (df['minutes'] < 15)]
    for index, row in rows_less15.iterrows():
        if row['match_id'] not in less15_match_ids[column]:
                less15_match_ids[column].append(row['match_id'])
            
    return dict(less15_match_ids)


def find_too_high_first(df, thresholds):
    high_start_match_ids = defaultdict(list)

    for index, row in df.iterrows():
        for column, threshold in thresholds.items():
            if isinstance(row[column],str):
                data_list = eval(row[column])
                if data_list and data_list[0] > threshold:
                    if row['match_id'] not in high_start_match_ids[column]:
                        high_start_match_ids[column].append(row['match_id'])
    
    return dict(high_start_match_ids)

def find_non_monotonic(df, columns):
    non_monotonic_match_ids = defaultdict(list)
    
    for index, row in df.iterrows():
        for column in columns:
            if isinstance(row[column],str):
                data_list = eval(row[column])
                if data_list and not all(x <= y for x, y in zip(data_list, data_list[1:])):
                    if row['match_id'] not in non_monotonic_match_ids[column]:
                        non_monotonic_match_ids[column].append(row['match_id'])
        
                
    return dict(non_monotonic_match_ids)  


def print_compact(data, cols=4):
    rows = len(data) // cols + (1 if len(data) % cols else 0)
    for i in range(rows):
        for j in range(cols):
            idx = i + j * rows
            if idx < len(data):
                print(f'{data[idx][0]:<30} > {data[idx][1]:<3}', end='  ')
        print()  # New line after finishing a row


def compute_invalid_ids_and_print(clean_details):
    invalid_match_ids = set()
    print('-------------------------')
    for key, dct in clean_details.items():
        print(f"Cleaning: [{key}]")
        column_data = [(col, len(lst)) for col, lst in dct.items()]
        
        # Use the compact print function
        print_compact(column_data, 4)  # You can adjust the number of columns as needed
        
        invalid_mids = set()
        for _, lst in dct.items():
            invalid_mids.update(lst)
        total_removed = len(invalid_mids)
        unique_removed = len(invalid_mids - invalid_match_ids)
        print(f"Total matches removed due to {key} : {total_removed} (+{unique_removed} unique)")
        print('-------------------------')
        invalid_match_ids.update(invalid_mids)
    return list(invalid_match_ids)


def keep_only_top_teams(df, teams_csv_path):
    team_ids = dotabet.utils.get_teams_ids(teams_csv_path)
    total_unique = df['match_id'].nunique()
    assert len(df)%10==0, f'all_player_csv matches do not have strictly 10 rows for each match {len(df)=}'
    
    sliced_df = df[df['player_team_id'].isin(team_ids)]
    assert len(sliced_df)%5==0, 'top teams didnt have exactly 5 rows for each match'

    print(f"(filter) Removed non-csv teams: {(len(df) - len(sliced_df))//5}/{total_unique} matches have a non-top opponent")
    return sliced_df

def get_match_minutes(element):
    if isinstance(element, str):
        return len(eval(element))
    else:
        return 0

def check_team_name_duplicates(df):

    # Find the most recent 'player_team_name' for each 'player_team_id'
    most_recent_name = df.drop_duplicates('player_team_id').set_index('player_team_id')['player_team_name'].to_dict()

    # Check and correct discrepancies
    for player_team_id in df['player_team_id'].unique():
        unique_names = df[df['player_team_id'] == player_team_id]['player_team_name'].unique()
        if len(unique_names) > 1:
            print(f"⚠️Two different names fo {player_team_id=}: {unique_names}. Keep only {most_recent_name[player_team_id]}!")
            df.loc[df['player_team_id'] == player_team_id, 'player_team_name'] = most_recent_name[player_team_id]

    return df


##### main 2 level clean function #####
def clean(all_player_csv_path, all_player_clean_csv_path, teams_csv_path):
    df = pd.read_csv(all_player_csv_path)
    df = keep_only_top_teams(df, teams_csv_path)
    print(f"Number of matches with csv teams before cleanup: {df['match_id'].nunique()}")

    clean_details = {
        "nan": {},
        "non_monotonic": {},
        "too_high_first": {},
        "more60": {},
        "less15" : {},
    }

    df['minutes'] = df['gold_t'].apply(get_match_minutes)
    
    clean_details["nan"] = find_nan(df)
    clean_details["too_high_first"] = find_too_high_first(df, {'gold_t': 1000, 'xp_t': 1000, 'lh_t': 10})
    clean_details["non_monotonic"] = find_non_monotonic(df, ['gold_t', 'xp_t', 'lh_t'])
    clean_details["more60"] = find_more60_minutes_match(df)
    clean_details["less15"] = find_less15_minutes_match(df)

    invalid_match_ids = compute_invalid_ids_and_print(clean_details)  
    print(f"TOTAL UNIQUE MATCHES TO CLEAN: {len(invalid_match_ids)} / {df['match_id'].nunique()} or {100*len(invalid_match_ids)/df['match_id'].nunique():.2f}%")
    df_cleaned = df[~df['match_id'].isin(invalid_match_ids)]
    print(f"FINAL NUMBER OF MATCHES: {df_cleaned['match_id'].nunique()}")
    df_cleaned = df_cleaned.sort_values(by='start_time', ascending=False)
    df_cleaned = check_team_name_duplicates(df_cleaned)

    with open("invalid_match_ids.json", "w") as file:
            json.dump(clean_details, file)
    with open("indexes_to_remove.json", "w") as file:
            json.dump(invalid_match_ids, file)

    df_cleaned.to_csv(all_player_clean_csv_path, index=False)
    