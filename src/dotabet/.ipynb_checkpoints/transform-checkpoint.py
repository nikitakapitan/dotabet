import pandas as pd


def normalize_and_sum(cumsum_teams_path, exclude_columns=['match_count','win','player_team_id', 'team_composition_id']):
    df = pd.read_csv(cumsum_teams_path)
    
    data_win_0 = df[df['win'] == 0]
    data_win_1 = df[df['win'] == 1]
    
    # Iterate over each numeric column
    for col in df.select_dtypes(include=['int', 'float']).columns:
        if col not in exclude_columns:
            # Calculate mean and standard deviation separately for 'win' 0 and 'win' 1
            avg_win_0 = data_win_0[col].mean()
            std_dev_win_0 = data_win_0[col].std()
            avg_win_1 = data_win_1[col].mean()
            std_dev_win_1 = data_win_1[col].std()
            
            # Normalize column values based on 'win' 0 data
            df.loc[df['win'] == 0, col] = (df.loc[df['win'] == 0, col] - avg_win_0) / std_dev_win_0
            # Normalize column values based on 'win' 1 data
            df.loc[df['win'] == 1, col] = (df.loc[df['win'] == 1, col] - avg_win_1) / std_dev_win_1
    
    # Create new column "norm" which is the sum of mentioned numeric columns (excluding excluded columns)
    numeric_columns = [col for col in df.select_dtypes(include=['int', 'float']).columns if col not in exclude_columns]
    # df['norm_sum'] = df[numeric_columns].sum(axis=1)
    df.insert(loc=5, column='norm_sum', value=df[numeric_columns].sum(axis=1))
    df.to_csv(cumsum_teams_path)
    print(f"Updated with 'norm_sum' : {cumsum_teams_path}")
