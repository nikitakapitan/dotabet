import matplotlib.pyplot as plt
import plotly.express as px
import dotabet
import pandas as pd

def plot_data_interactive(df, win_value, x_axis, values, labels):
    # Filter the DataFrame based on 'win' value
    plot_df = df[df['win'] == win_value]

    # Pivot table to format data for plotting
    plot_df = plot_df.pivot_table(index=x_axis, columns=labels, values=values, aggfunc='mean')
    
    # Reset index to make 'mov_avg_end_date' a column again
    plot_df = plot_df.reset_index()

    # Melting DataFrame for Plotly
    plot_df = plot_df.melt(id_vars=['mov_avg_end_date'], var_name='Item', value_name='Normalized Sum')

    # Creating the plot
    fig = px.line(plot_df, x='mov_avg_end_date', y='Normalized Sum', color='Item', 
                  title=f'Time Series Plot for win = {win_value}', markers=True,
                  labels={'mov_avg_end_name': 'Date', 'Normalized Sum': 'Normalized Sum'})
    
    # Enhancing the layout
    fig.update_layout(xaxis_title='Date',
                      yaxis_title='Normalized Sum',
                      legend_title='Item',
                      width=1000,
                      height=600,
                      xaxis=dict(tickformat="%Y-%m-%d"))
    fig.show()

def plot_teams_perf_over_time(cumsum_teams_path, target_column):
    df = pd.read_csv(cumsum_teams_path)
    df['mov_avg_end_date'] = pd.to_datetime(df['mov_avg_end_date'])
    
    for win in [0,1]:
        plot_data_interactive(df, win_value=win, x_axis='mov_avg_end_date', values=target_column, labels='player_team_name')

def plot_players_perf_over_time(cumsum_players_path, target_column):
    df = pd.read_csv(cumsum_players_path)
    df['mov_avg_end_date'] = pd.to_datetime(df['mov_avg_end_date'])
    
    for win in [0,1]:
        plot_data_interactive(df, win_value=win, x_axis='mov_avg_end_date', values=target_column, labels='player_name')