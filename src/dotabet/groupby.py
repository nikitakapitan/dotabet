import pandas as pd
import dotabet
import os

numeric_features = ['actions_per_min', 'ancient_kills', 'assists', 'camps_stacked', 'deaths', 'denies', 'gold_per_min', 'hero_damage', 'hero_healing', 'hero_id', 'hero_kills', 'kda', 'lane_efficiency', 'win', 'last_hits', 'net_worth', 'neutral_kills', 'observer_kills', 'roshan_kills', 'rune_pickups', 'sentry_kills', 'sen_placed', 'teamfight_participation', 'total_gold', 'total_xp', 'tower_damage', 'tower_kills', 'xp_per_min']

def groupby_team_composition(features_csv_path):

    df = pd.read_csv(features_csv_path)

    str_col_to_keep = [
    # 'player_name',
    # 'start_time',
    # 'league_name',
    'player_team_name',
    # 'radiant_name',
    # 'dire_name' ,
    'team_composition',
    ]
    
    num_col_to_keep = [
        'player_team_id',
        # 'match_id',
        # 'account_id',
        # 'hero_id',
        # 'win',
        # 'leagueid',
        # 'player_position',
        'team_composition_id',
    ] + numeric_features
 
    df = df[str_col_to_keep + num_col_to_keep]

    str_agg = lambda x: x.mode()[0] if not x.empty else None
    agg_dict = {col: 'mean' for col in num_col_to_keep}  
    agg_dict.update({col: str_agg for col in str_col_to_keep}) 
    
    teamsgr = df.groupby('team_composition_id') 
    teams = teamsgr.agg(agg_dict)
    teams['count'] = teamsgr.size()

    teams = teams.reindex(columns=str_col_to_keep + ['count'] + num_col_to_keep)
    teams.reset_index(drop=True, inplace=True)
    teams = teams.sort_values(by='player_team_id', ascending=False)
    teams.to_csv(os.path.join(os.path.dirname(features_csv_path), "composed_teams.csv"))

def groupby_players(features_csv_path):
    str_col_to_drop = ['start_time', 'league_name', ]
    num_col_to_drop = ['leagueid', 'hero_id', 'account_id', 'match_id']
    
    df = pd.read_csv(features_csv_path)
    df = df.drop(columns=num_col_to_drop)

    # TODO

def groupby_matches(features_csv_path):

    df = pd.read_csv(features_csv_path)

    str_col_to_keep = [
    # 'player_name',
    # 'player_team_name',
    'start_time',
    'league_name',
    'radiant_name',
    'dire_name',
    # 'team_composition',
    'radiant_win',
    ]
    
    num_col_to_keep = [
        # 'player_team_id',
        'match_id',
        # 'account_id',
        # 'hero_id',
        'radiant_win',
        'leagueid',
        'radiant_team_id',
        'dire_team_id',
        # 'player_position',
        # 'team_composition_id',
    ]
    
    df = df[str_col_to_keep + num_col_to_keep]
    
    num_cols = df.select_dtypes(include=['int', 'float']).columns
    str_cols = df.select_dtypes(include=['object']).columns

    str_agg = lambda x: x.mode()[0] if not x.empty else None
    agg_dict = {col: 'mean' for col in num_cols}  
    agg_dict.update({col: str_agg for col in str_cols}) 
    
    teamsgr = df.groupby('team_composition_id') 
    teams = teamsgr.agg(agg_dict)
    teams['count'] = teamsgr.size()
    
    teams.to_csv(os.path.join(os.path.dirname(features_csv_path), "composed_teams.csv"))

