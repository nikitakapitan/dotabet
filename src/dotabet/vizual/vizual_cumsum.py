import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def _plot_team_data_intervals(merged_df):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Unique teams and their compositions
    unique_teams = merged_df[['player_team_name', 'team_composition']].drop_duplicates()
    unique_teams.to_csv(r'D:\WORKSPACE\dotabet\data\top_teams\trace\vizual_cumsum.unique_teams.csv')
    
    # Plotting the time intervals for each team
    for _, team_info in unique_teams.iterrows():
        team = team_info['player_team_name']
        composition = team_info['team_composition']
        
        team_data = merged_df[merged_df['player_team_name'] == team]
        for _, row in team_data.iterrows():
            ax.plot([row['cumsum_from'], row['cumsum_up_to']], [team, team], linewidth=8)
            # Adding match count annotation with black color
            ax.text(row['cumsum_from'], team, f"{row['match_count']}", ha='left', va='center', fontsize=10, color='black', weight='bold')
        
        # Adding team composition text below the team name
        ax.text(merged_df['cumsum_from'].min(), team, f"\n{composition}", ha='left', va='bottom', fontsize=8, color='gray')

    # Formatting the x-axis to show dates
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    
    # Adding labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Team Name')
    ax.set_title('Available Time Periods and Match Counts for Each Team')
    
    # Show grid for better readability
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    plt.show()


def plot_cumsum_intervals(cumsum_team_composition_path):
    cumsum_df = pd.read_csv(cumsum_team_composition_path)
    
    cumsum_df['cumsum_from'] = pd.to_datetime(cumsum_df['cumsum_from'])
    cumsum_df['cumsum_up_to'] = pd.to_datetime(cumsum_df['cumsum_up_to'])
    
    # If 'cumsum_up_to' is NaN, replace it with today's date
    cumsum_df['cumsum_up_to'].fillna(pd.Timestamp.today(), inplace=True)
    

    merged_df = cumsum_df.groupby(['player_team_name', 'cumsum_from', 'cumsum_up_to', 'team_composition']).apply(format_match_counts).reset_index(name='match_count')
    merged_df.to_csv(r'D:\WORKSPACE\dotabet\data\top_teams\trace\vizual_cumsum.merged_df.csv')
    _plot_team_data_intervals(merged_df)

def format_match_counts(group):
    win_count = group[group['win'] == 1]['match_count'].sum()
    loss_count = group[group['win'] == 0]['match_count'].sum()
    if win_count and loss_count:
        return f"(W:{win_count}, L:{loss_count})"
    elif win_count:
        return f"(W:{win_count}, L:0)"
    else:
        return f"(W:0, L:{loss_count})"



