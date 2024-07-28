import plotly.express as px
import pandas as pd
from datetime import datetime
import dotabet
from plotly.subplots import make_subplots

features_csv_path = r"D:\WORKSPACE\dotabet\data\top_teams\features.csv"
teams_csv_path = r"D:\WORKSPACE\dotabet\constants\teams.csv"

def plot_timeline():

    df = pd.read_csv(features_csv_path)
    top_ids = dotabet.utils.get_teams_ids(teams_csv_path, top_teams=True)
    df = df[df['player_team_id'].isin(top_ids)]
    df['team_composition_id'] = df['team_composition_id'].astype('Int64')
    
    # Convert start_time to datetime
    df['start_time'] = pd.to_datetime(df['start_time'])
    
    grouped = df.groupby(['player_team_id', 'team_composition_id'])['start_time'].agg(['min', 'max']).reset_index()
    
    # Rename columns for clarity
    grouped.rename(columns={'min': 'composition_start_time', 'max': 'composition_end_time'}, inplace=True)
    
    grouped.loc[grouped['composition_start_time'] == grouped['composition_end_time'], 'composition_end_time'] += pd.Timedelta(weeks=1)
    
    # Merge the computed start and end times back into the original dataframe
    df = df.merge(grouped, on=['player_team_id', 'team_composition_id'], how='left')
    
    # Handle the case where the composition changes back to an old one
    df['composition_end_time'] = df.groupby(['player_team_id', 'team_composition_id'])['composition_end_time'].transform('max')
    
    df.to_csv(r'D:\WORKSPACE\dotabet\data\top_teams\trace\colab.df.csv')
    
    
    # Create a new DataFrame with unique team compositions per team
    team_compositions = df[['player_team_name', 'team_composition_id', 'team_composition', 'composition_start_time', 'composition_end_time', 'player_team_id']].drop_duplicates()
    
    # Calculate match count for each team composition
    team_compositions['match_count'] = df.groupby(['player_team_name', 'team_composition_id'])['match_id'].transform('count')//5
    
    # Plotting with Plotly
    fig = make_subplots(rows=1, cols=1)
    
    # Unique teams and their compositions
    unique_teams = team_compositions[['player_team_name', 'team_composition_id', 'team_composition']].drop_duplicates()
    
    unique_teams.to_csv(r'D:\WORKSPACE\dotabet\data\top_teams\trace\colab.unique_teams.csv')
    team_compositions.to_csv(r'D:\WORKSPACE\dotabet\data\top_teams\trace\colab.team_compositions.csv')
    
    ###############################################################################################
    
    df = pd.read_csv(r"D:\WORKSPACE\dotabet\data\top_teams\trace\colab.team_compositions.csv")
    
    for date_col in ['composition_start_time', 'composition_end_time']:
        df[date_col] = pd.to_datetime(df[date_col])
    
    df['composition_start_time_str'] = df['composition_start_time'].dt.strftime('%d-%m-%y')
    df['composition_end_time_str'] = df['composition_end_time'].dt.strftime('%d-%m-%y')
    
    # df['team_composition_unique_id'] = df['player_team_name'] + '-' + df['team_composition_id'].astype(str)
    df = df.sort_values(by='player_team_name', key=lambda col: col.str.lower(), ascending=True)
    
    # Plotting
    fig = px.timeline(
        df, 
        x_start="composition_start_time", 
        x_end="composition_end_time", 
        y="player_team_name", 
        color="player_team_name",
        hover_data={
            "team_composition": True,
            "match_count": True,
            "team_composition_id": True,
            "composition_start_time_str": True,
            "composition_end_time_str": True,
            "player_team_id": True
        },
        title="Evolution of Team Compositions Over Time"
    )
    
    
    fig.add_vline(x=datetime(2023, 10, 12).timestamp() * 1000, line_width=2, line_dash="dash", line_color="red", annotation_text="TI 2023", annotation_position="top")
    fig.add_vline(x=datetime(2024, 9, 4).timestamp() * 1000, line_width=2, line_dash="dash", line_color="blue", annotation_text="TI 2024", annotation_position="top")
    fig.add_vline(x=datetime.today().timestamp() * 1000, line_width=2, line_dash="dash", line_color="green", annotation_text="Today", annotation_position="top")
    
    
    fig.update_layout(
        xaxis=dict(
            tickformat='%b-%y'
        ),
        yaxis_title='Teams',
        xaxis_title='Time',
        width=1600,
        height=900
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>team_id: %{customdata[5]}<br>Start: %{customdata[3]}<br>End: %{customdata[4]}<br>Matches: %{customdata[1]}<br>Comp. ID: %{customdata[2]}<br>Composition: %{customdata[0]}'
    )
    
    fig.show()