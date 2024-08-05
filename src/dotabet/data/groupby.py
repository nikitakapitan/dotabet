import pandas as pd
import dotabet
import os

# if groupby == 'team_composition_id' ----> ONLY player_lvl_featuers
player_lvl_featuers = ['account_id', 'player_name', 'hero_id', 'player_position']
# if groupby == 'match_id' ---> player_lvl_featuers + team_lvl_features
team_lvl_features = ['player_team_name', 'team_composition', 'win', 'player_team_id', 'team_composition_id',]  
# if ...
match_lvl_features = ['match_id', 'start_time', 'league_name', 'radiant_name', 'dire_name', 'radiant_team_id', 'dire_team_id']

numeric_features = ['actions_per_min', 'ancient_kills', 'assists', 'camps_stacked', 'deaths', 'denies', 'gold_per_min', 
                    'hero_damage', 'hero_healing',  'hero_kills', 'kda', 'lane_efficiency', 'last_hits', 'net_worth', 
                    'neutral_kills', 'observer_kills', 'roshan_kills', 'rune_pickups', 'sentry_kills', 'sen_placed', 
                    'teamfight_participation', 'total_gold', 'total_xp', 'tower_damage', 'tower_kills', 'xp_per_min'] +\
                     [ f"{ft}{k}" for k in [10,15,20,25,30] for ft in ['gold', 'xp', 'lh'] ]

def groupby_matches_and_teams(features_csv_path):

    df = pd.read_csv(features_csv_path)  
    df = df[match_lvl_features + team_lvl_features + numeric_features]

    str_agg = lambda x: x.mode()[0] if not x.empty else None
    agg_dict = {col: 'mean' for col in df.select_dtypes(include=['int', 'float']).columns}  
    agg_dict.update({col: str_agg for col in df.select_dtypes(include=['object']).columns}) 
    
    df_gr = df.groupby(['match_id', 'player_team_id']) 
    df = df_gr.agg(agg_dict)
    
    df.to_csv(os.path.join(os.path.dirname(features_csv_path), "composed_teams.csv"))

    dir_name, file_name = os.path.split(features_csv_path)

    df = df.drop(['match_id', 'player_team_id'], axis=1)
    df = df.reset_index()
    df['win'] = df['win'].astype(bool)
    df.to_csv(os.path.join(dir_name, os.path.splitext(file_name)[0] + '_by_matches_and_teams.csv'))
    return df

def groupby_team_composition(features_csv_path, teams_csv_path=None):
    # if teams_csv_path provided => return only current teams

    df = pd.read_csv(features_csv_path)
    if teams_csv_path: # filter by current teams only
        const_teams_df = pd.read_csv(teams_csv_path)
        df = df[df['team_composition_id'].isin(const_teams_df['team_composition_id'].values)]
        
    teams = _groupby_team_composition(df)
    teams = teams.sort_values(by=['win', 'player_team_id'])

    new_filename = "composed_teams.csv"
    teams.to_csv(os.path.join(os.path.dirname(features_csv_path), new_filename))
    print(f"Created: {new_filename}")

def _groupby_team_composition(df):
    df = df[team_lvl_features + numeric_features]

    # str_agg = lambda x: x.mode()[0] if not x.empty else None
    # agg_dict = {col: 'mean' for col in df.select_dtypes(include=['int', 'float']).columns}  
    # agg_dict.update({col: str_agg for col in df.select_dtypes(include=['object']).columns}) 
    agg_dict = get_agg_dict(df, groupby_columns=['team_composition_id', 'win'], ignore_columns=player_lvl_featuers)
    
    teamsgr = df.groupby(['team_composition_id', 'win']) 
    teams = teamsgr.agg(agg_dict)
    teams['match_count'] = teamsgr.size() //5

    teams = teams.reset_index()
    teams = teams.reindex(columns=['match_count'] + team_lvl_features + numeric_features)
    return teams

def groupby_account(features_csv_path, teams_csv_path=None):
    # if teams_csv_path provided => return only current teams

    df = pd.read_csv(features_csv_path)
    if teams_csv_path: 
        account_ids = dotabet.utils.get_account_ids(teams_csv_path)
        df = df[df['account_id'].isin(account_ids)]
        
    players = _groupby_account(df)

    new_filename = "players.csv"
    players.to_csv(os.path.join(os.path.dirname(features_csv_path), new_filename))
    print(f"Created: {new_filename}")

def _groupby_account(df):
    # keep these columns:
    df = df[['account_id', 'player_name', 'player_position'] + ['win'] + numeric_features]

    def exp_avg(series):
        return series.ewm(span=len(series), adjust=False).mean().iloc[-1]

    str_agg = lambda x: x.mode()[0] if not x.empty else None
    agg_dict = {col: 'mean' for col in df.select_dtypes(include=['int', 'float']).columns} # 'mean' or exp_avg
    agg_dict.update({col: str_agg for col in df.select_dtypes(include=['object']).columns}) 

    accountsgr = df.groupby(['account_id', 'win'])
    players = accountsgr.agg(agg_dict)
    players.insert(loc=0, column='match_count', value=accountsgr.size()) 

    players.reset_index(drop=True, inplace=True)
    return players
    

def dotabet_aggregator(series, ignore_columns):
    if series.name in ignore_columns:
        return "DUMMY"
    elif pd.api.types.is_numeric_dtype(series):
        return series.mean()
    elif pd.api.types.is_string_dtype(series):  # Assuming string columns have dtype 'object'
        if len(series.unique()) > 1:
            raise ValueError(f"Inconsistent values found in {series.name}: {series.unique()}")
        return series.iloc[0]
    else:
        if len(series.unique()) > 1:
            raise ValueError(f"Inconsistent values found in {series.name=} ({series.dtype=}) : {series.unique()}")
        return series.iloc[0]

def get_agg_dict(df, groupby_columns, ignore_columns):
    """Return the rule on how to aggregate df:
    - float or int -> MEAN
    - object (str) -> iloc[0] (+ unique check)
    - else -> iloc[0]
    """
    agg_dict = {}
    for col in df.columns:
        if col in groupby_columns:
            continue  # Skip the grouping column
        agg_dict[col] = lambda x : dotabet_aggregator(x, ignore_columns)
    return agg_dict


