import pandas as pd

def get_features_asof(df, asof_date, min_matches, team_composition_id):
    df = df[df['start_time'] < asof_date]
    df = df[df['team_composition_id'] == team_composition_id]
    if df['match_id'].nunique() >= min_matches:
        return dotabet.groupby._groupby_team_composition(df)
    else:
        print(f"🛑 cumsum.py: matches nunique={df['match_id'].nunique()} < 30 matches to compute features asof. Skiping..")

    

def prepare_train_data(features_csv_path, min_matches=30, teams_csv_path=None):
    """
    min_matches: how many matches required to compute the output (if not so many mathces, team will be skipped)

    if teams_csv_path: filter df by ids from the csv only
    """
    df = pd.read_csv(features_csv_path)
    df['start_time'] = df['start_time'].apply(lambda x : datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    
    if teams_csv_path: # filter by only current teams
        current_ids = dotabet.utils.get_teams_composition_ids(teams_csv_path)
        df = df[df['team_composition_id'].isin(current_ids)]

    groupby_columns = ['match_id']
    ignore_columns = dotabet.groupby.player_lvl_featuers + dotabet.groupby.team_lvl_features
    agg_dict = dotabet.groupby.get_agg_dict(df, groupby_columns, ignore_columns=ignore_columns)
    match_df = df.groupby(groupby_columns).agg(agg_dict)
        
    train_df = pd.DataFrame()
    match_df = match_df.sort_values(by='start_time', ascending=True)
    match_df = match_df[['start_time','dire_team_id','radiant_team_id','radiant_win',]]

    for idx, row in match_df.iterrows(): 
        if row['start_time'].year >= 2024 and row['start_time'].month >= 3:
            # Radiant
            radiant_team_id = int(row['radiant_team_id'])
            radiant_team_composition_id = dotabet.utils.get_team_composition_id(radiant_team_id)
            radiant_features_asof = get_features_asof(df, row['start_time'], min_matches, radiant_team_composition_id)
            # Dire
            dire_team_id = int(row['dire_team_id'])
            dire_team_composition_id = dotabet.utils.get_team_composition_id(dire_team_id)
            dire_features_asof = get_features_asof(df, row['start_time'], min_matches, dire_team_composition_id)
            
            if radiant_features_asof is not None:
                train_df = pd.concat([train_df, radiant_features_asof], ignore_index=True)
            if dire_features_asof is not None:
                train_df = pd.concat([train_df, dire_features_asof], ignore_index=True)

    train_df.to_csv(r"D:\WORKSPACE\dotabet\data\top_teams\cumsum\train_df.csv")
    return train_df