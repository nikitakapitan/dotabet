import pandas as pd
import dotabet
import os
from datetime import datetime

def make_cumsum(features_csv_path, by, teams_csv_path=None, window_months=9, step_months = 3):
    """
    by : str . Options: ['team_composition_id', 'account_id']

    if teams_csv_path: filter df by ids from the csv only
    """
    if by == 'team_composition_id':
        if teams_csv_path:
            current_ids = dotabet.utils.get_teams_composition_ids(teams_csv_path, top=True)
        groupby_func = dotabet.groupby._groupby_team_composition
    elif by == 'account_id':
        if teams_csv_path:
            current_ids = dotabet.utils.get_account_ids(teams_csv_path)
        groupby_func = dotabet.groupby._groupby_account
    
    df = pd.read_csv(features_csv_path)
    df[by] = df[by].astype(int)

    print(f"cumsum.py INFO: <Initial> {df[by].nunique()=} {len(df)=}")
    if teams_csv_path: 
        df = df[df[by].isin(current_ids)]
    print(f"cumsum.py INFO: <Filtred ids> {df[by].nunique()=} {len(df)=}")

    df['start_time'] = pd.to_datetime(df['start_time'])
    df.sort_values('start_time', ascending=False, inplace=True)
    
    min_date = df['start_time'].min()
    max_date = df['start_time'].max()
    
    start_period = min_date
    
    # Define fixed time intervals
    intervals = [
        (min_date, datetime(2023, 12, 1)),
        (datetime(2023, 12, 1, 0, 1), datetime(2024, 3, 1)),
    ]
    
    if max_date < datetime(2024, 9, 1):
        intervals.append((datetime(2024, 3, 1, 0, 1), max_date))
    else:
        intervals.append((datetime(2024, 3, 1, 0, 1), datetime(2024, 7, 1)))
        intervals.append((datetime(2024, 7, 1, 0, 1), max_date))

    cumsum_df_list = []
    
    for start_period, end_period in intervals:
    
        period_df = df[(df['start_time'] >= start_period) & (df['start_time'] < end_period)]
            
        assert not period_df.empty, f"cumsum.py: empty period_df. Check dates. {start_period=} {end_period=} "
        period_group_df = groupby_func(period_df)
        period_group_df.insert(loc=4, column='cumsum_from', value=start_period.strftime('%Y-%m-%d'))
        period_group_df.insert(loc=5, column='cumsum_up_to', value=end_period.strftime('%Y-%m-%d'))
        cumsum_df_list.append(period_group_df)
        
    cumsum_df = pd.concat(cumsum_df_list, ignore_index=True)
    cumsum_df = cumsum_df[cumsum_df['match_count'] >=1 ]

    # re-arrange columns & sort
    if by == 'team_composition_id':
        cumsum_df = cumsum_df.sort_values(by=['cumsum_from', by, 'win'])
    elif by == 'account_id':
        first_cols = ['player_name', 'account_id', 'cumsum_from', 'cumsum_up_to', 'match_count', 'win']
        remaining_cols = [col for col in cumsum_df.columns if col not in first_cols]
        cumsum_df = cumsum_df[first_cols + remaining_cols]
        cumsum_df = cumsum_df.sort_values(by=['account_id', 'cumsum_from', 'win'])


    new_file_path = os.path.join(os.path.dirname(features_csv_path), 'cumsum', f"by_{by}_window{window_months}_step{step_months}.csv")
    cumsum_df.to_csv(new_file_path)
    print(f"Created: {new_file_path}")
    return cumsum_df


# import dotabet
# WINDOW_MONTH = 6
# STEP_MONTHS = 1

# # top_teams/features.csv -> top_teams/cumsum/by_..._windowX_stepY.csv
# debug_cumsum_df = dotabet.cumsum.make_cumsum(dotabet.features_csv_path, 'account_id', teams_csv_path=None, window_months=WINDOW_MONTH, step_months = STEP_MONTHS) 