import dotabet
import pandas as pd

def get_elo_win_proba(df):
    max_rating = df['rating'].max()
    df['elo_win_proba'] = (1 / (1 + 10 ** ((max_rating - df['rating']) / 400)))
    df['elo_win_proba'] /= df['elo_win_proba'].sum()
    df['elo_coef'] = 1/df['elo_win_proba']
    return df


def prepare_league_teams_csv(LEAGUE_ID,  teams_csv_path, league_teams_csv_path):
    
    data = dotabet.fetch.fetch_data(f"https://api.opendota.com/api/leagues/{LEAGUE_ID}/teams")
    league_df = pd.DataFrame(data)
    constants_df = pd.read_csv(teams_csv_path)

    merged_df = pd.merge(league_df, constants_df, on='team_id')#, suffixes=('_proj', '_const'))
    df = merged_df.drop('logo_url', axis=1)

    df = get_elo_win_proba(df)
    df = df.sort_values(by='rating', ascending=False)
    
    # check league's teams compositions are up-to-date
    dotabet.consistency.check_team_composition_id_team_csv_against_api(df)
    
    df.to_csv(league_teams_csv_path, index=False)

    

    
