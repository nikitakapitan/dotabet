

def check_missing_data(features_df):
    if features_df['missing_data'].any():
        print("❌ features.csv contains missing data")
    else:
        print(f"features.csv (1/3).✅No missing data")

def check_unique_composition(features_df):
    df = features_df
    bug = False
    for compos_id in df['team_composition_id'].unique():
        sliced_df = df[df['team_composition_id'] == compos_id]
        unique_accounts = sliced_df['account_id'].nunique()
        if not (unique_accounts == 5):
            print(f"❌ {sliced_df['player_team_name']} with {compos_id=} has {unique_accounts=}"); bug=True;
    if not bug:
        print(f"features.csv (2/3)✅For each composition team, all matches has only 5 different accounts")


def check_5rows_consistency(features_df, only10rows:bool):
    """
    1. each match (match_id) has exactly 10 rows
    2. each match has exacly 2 different player_team_id
    3. each player_team_id within match, has exactly 5 rows (5 players)
    4. these 5 rows has exactly 5 different account_id
    """
    df = features_df
    bug = False
    
    for match_id, match_data in df.groupby('match_id'):
        team_ids = match_data['player_team_id'].unique()
        
        if only10rows:
            if len(match_data) != 10:
                print(f"❌Match ID {match_id} does not have exactly 10 players."); bug=True;
            if set(match_data['win'].unique()) != {0, 1}:
                print(f"❌match ID {match_id} all teams loose or win ('win' is 0 or 1 for both teams)"); bug=True;
            if len(team_ids) != 2:
                print(f"❌Match ID {match_id} does not have exactly 2 teams."); bug=True;
        
        for team_id in team_ids:
            team_data = match_data[match_data['player_team_id'] == team_id]
            if len(team_data) != 5:
                print(f"❌Team ID {team_id} in match ID {match_id} does not have exactly 5 players."); bug=True;
            if len(team_data['account_id'].unique()) != 5:
                print(f"❌Team ID {team_id} in match ID {match_id} has duplicate account IDs."); bug=True;
            if len(team_data['win'].unique()) != 1:
                print(f"❌Team ID {team_id} in match ID {match_id} has 0 and 1 'win' values"); bug=True;
            # if set(team_data['player_position']) != set([1,2,3,4,5]):
            #     print(f"❌Team ID {team_id} in match ID {match_id} doesnt have 12345 positions"); bug=True;
    if not bug:            
        print(f"features.csv (3/3)✅ has passed 10rows-consistency") 