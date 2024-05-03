import pandas as pd
import dotabet
import os

player_lvl_featuers = ['account_id', 'player_name', 'hero_id', 'player_position']
team_lvl_features = ['player_team_name', 'team_composition', 'player_team_id', 'team_composition_id', 'win',]
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


def groupby_team_composition(features_csv_path):

    df = pd.read_csv(features_csv_path)
    df = df[team_lvl_features + numeric_features]

    str_agg = lambda x: x.mode()[0] if not x.empty else None
    agg_dict = {col: 'mean' for col in df.select_dtypes(include=['int', 'float']).columns}  
    agg_dict.update({col: str_agg for col in df.select_dtypes(include=['object']).columns}) 
    
    teamsgr = df.groupby('team_composition_id') 
    teams = teamsgr.agg(agg_dict)
    teams['match_count'] = teamsgr.size() //5

    teams = teams.reindex(columns=str_col_to_keep + ['match_count'] + num_col_to_keep)
    teams.reset_index(drop=True, inplace=True)
    teams = teams.sort_values(by='player_team_id', ascending=False)
    teams.to_csv(os.path.join(os.path.dirname(features_csv_path), "composed_teams.csv"))

def groupby_players(features_csv_path):
    str_col_to_drop = ['start_time', 'league_name', ]
    num_col_to_drop = ['leagueid', 'hero_id', 'account_id', 'match_id']
    
    df = pd.read_csv(features_csv_path)
    df = df.drop(columns=num_col_to_drop)

    # TODO

