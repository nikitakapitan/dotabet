import pandas as pd

def check_all_values_not_nan(players_df):
    bug = False;
    
    for index, row in players_df.iterrows():
        for column in players_df.columns:
            if pd.isna(row[column]):
                print(f"❌ NaN found in column '{column}' for match_id '{row['match_id']}'"); bug=True;

    if not bug:
        print(f"all_players_clean.csv (1/1) ✅ features doesnt have any NaN")