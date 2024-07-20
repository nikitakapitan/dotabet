import pandas as pd
from dotabet.consistency.teams_csv import _check_teams_csv_posID_and_name_against_open_dota_api,\
                                        check_team_composition_id_team_csv_against_api,\
                                        _check_team_names_in_teams_csv_match_team_name_in_recent_features_data

def check_team_csv_consistency(teams_csv_path, features_csv_path, logs=False):
    features_df = pd.read_csv(features_csv_path)
    teams_df = pd.read_csv(teams_csv_path)
    
    _check_teams_csv_posID_and_name_against_open_dota_api(teams_df, logs=False)
    check_team_composition_id_team_csv_against_api(teams_df, features_df, logs=False)
    _check_team_names_in_teams_csv_match_team_name_in_recent_features_data(teams_df, features_df, logs=False)

from dotabet.consistency.apcsv import check_all_matches_has_exactly_10_rows
def check_all_player_csv_consistency(all_player_csv_path):
    raw_players_df = pd.read_csv(all_player_csv_path)
    check_all_matches_has_exactly_10_rows(raw_players_df)

from dotabet.consistency.clean_apcsv import check_all_values_not_nan
def check_all_player_clean_csv_consistency(all_player_clean_csv_path):
    players_df = pd.read_csv(all_player_clean_csv_path)
    check_all_values_not_nan(players_df)

from dotabet.consistency.features_csv import check_missing_data, check_unique_composition, check_5rows_consistency
def check_features_consistency(features_csv_path, only10rows=True):
    features_df = pd.read_csv(features_csv_path)

    check_missing_data(features_df)
    check_unique_composition(features_df)
    check_5rows_consistency(features_df, only10rows)



    