import pandas as pd
import dotabet
import os
from datetime import datetime

def make_cumsum(features_csv_path, by, teams_csv_path=None, window_months=9, step_months = 3):
    raise dotabet.DepricatedCode("Today we compute cumsum directly by request. Old code: dotabet.legacy.cumsum")


def make_player_cumsum(features_df, account_id, start_time, match_count=20):
    """
    Generate a cumulative sum DataFrame for a specific player given their account_id and start_time.
    The DataFrame will include the most recent data up to the specified start_time, ensuring that the
    'match_count' matches the specified value, otherwise maximum available data is used.

    :param features_csv_path: str, path to the features CSV file.
    :param account_id: int, account ID of the player.
    :param start_time: str, start time in the format 'YYYY-MM-DD HH:MM:SS'.
    :param match_count: int, the number of matches to include in the cumulative sum.
    :return: DataFrame, cumulative sum DataFrame for the specified player.
    """
    df = features_df

    # Filter the DataFrame for the specified account ID and start time
    player_df = df[(df['account_id'] == account_id) & (df['start_time'] < start_time)]

    if player_df.empty:
        return player_df
    
    # Sort by start_time
    player_df = player_df.sort_values('start_time', ascending=False)
    
    # Select the most recent matches up to the specified match count
    player_df = player_df.head(match_count)
    
    # Calculate the cumulative sum for the selected matches
    cumsum_df = dotabet.groupby._groupby_account(player_df)
    
    # Add columns for cumsum_from and cumsum_up_to
    cumsum_df.insert(loc=4, column='cumsum_from', value=player_df['start_time'].min().strftime('%Y-%m-%d'))
    cumsum_df.insert(loc=5, column='cumsum_up_to', value=player_df['start_time'].max().strftime('%Y-%m-%d'))

    # Re-arrange columns & sort
    first_cols = ['player_name', 'account_id', 'cumsum_from', 'cumsum_up_to', 'match_count', 'win']
    remaining_cols = [col for col in cumsum_df.columns if col not in first_cols]
    cumsum_df = cumsum_df[first_cols + remaining_cols]

    return cumsum_df

        
    
