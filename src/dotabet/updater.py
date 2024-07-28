import pandas as pd
from dotabet import utils
from datetime import datetime

timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M")

def log_message(message):
    log_entry = f'{timestamp}: "{message}"'
    with open("D:\WORKSPACE\dotabet\constants\logs.txt", "a", encoding='utf-8') as log_file:
        log_file.write(log_entry + "\n")
    print(log_entry)

def update_teams_csv(features_csv_path, teams_csv_path):
    # Load data
    features_df = pd.read_csv(features_csv_path)
    teams_df = pd.read_csv(teams_csv_path)
    teams_df.to_csv(fr"D:\WORKSPACE\dotabet\constants\backup\teams_{timestamp}.csv", index=False)
    int_cols = ['Pos1ID', 'Pos2ID', 'Pos3ID', 'Pos4ID', 'Pos5ID', 'team_composition_id']
    teams_df[int_cols] = teams_df[int_cols].astype('Int64')
    
    top_teams_df = teams_df[teams_df['top'] == 1]
    problem = False

    
    for _, team_row in top_teams_df.iterrows():
        team_id = team_row['team_id']
        team_composition_id = team_row['team_composition_id']
        team_csv_player_ids = {
            team_row['Pos1']: int(team_row['Pos1ID']),
            team_row['Pos2']: int(team_row['Pos2ID']),
            team_row['Pos3']: int(team_row['Pos3ID']),
            team_row['Pos4']: int(team_row['Pos4ID']),
            team_row['Pos5']: int(team_row['Pos5ID'])
        }

        # Assert sum of values
        assert sum(team_csv_player_ids.values()) == team_composition_id,\
        f"Team composition ID mismatch for team {team_id}: sum csv = ({sum(team_csv_player_ids.values())}) VS team_composition_id ({team_composition_id})"

        # Filter and sort features_df by start_time
        team_matches = features_df[features_df['player_team_id'] == team_id]
        if team_matches.empty:
            continue

        team_matches = team_matches.sort_values(by='start_time', ascending=False)
        most_recent_match_id = team_matches.iloc[0]['match_id']
        recent_match_players = team_matches[team_matches['match_id'] == most_recent_match_id].head(5)

        assert len(recent_match_players) == 5, "Expected 5 players for the recent match"

        # Create set of player IDs from the features
        features_player_ids = set(recent_match_players['account_id'].astype(int))
        
        # Compute team_composition_id from features
        computed_team_composition_id = sum(features_player_ids)
        
        if computed_team_composition_id != team_composition_id:
            # Check differences
            team_csv_player_ids_set = set(team_csv_player_ids.values())
            diff_ids = team_csv_player_ids_set.symmetric_difference(features_player_ids)
            assert len(diff_ids) >= 2, "dotabet/updater: team_composition_id are different, but players are all the same"
            
            if len(diff_ids) == 2:
                active_id = list(features_player_ids - team_csv_player_ids_set).pop()
                inactive_id = list(team_csv_player_ids_set - features_player_ids).pop()
                pos_to_update = list(team_csv_player_ids.values()).index(inactive_id) + 1  # +1 to match Pos{x}ID format
                pos_to_update_str = f'Pos{pos_to_update}ID'
                top_teams_df.loc[top_teams_df['team_id'] == team_id, pos_to_update_str] = active_id
                top_teams_df.loc[top_teams_df['team_id'] == team_id, 'team_composition_id'] = computed_team_composition_id
                top_teams_df.loc[top_teams_df['team_id'] == team_id, f'Pos{pos_to_update}'] = utils.fetch_player_name(active_id)
                log_message(f"🔄✔️Updated {pos_to_update_str} for team {team_row['team_name']}({team_id}) with player {utils.fetch_player_name(active_id)}({active_id}). \
                {team_composition_id=} -> {computed_team_composition_id=}")

            else:
                problem = True
                current_ids = team_csv_player_ids_set - features_player_ids
                new_ids = features_player_ids - team_csv_player_ids_set
                current_info = [(name, val) for name, val in team_csv_player_ids.items() if val in current_ids]
                new_info = [(utils.fetch_player_name(val), val) for val in new_ids]

                log_message(f"⚠️ Multiple differences found for team {team_row['team_name']} {team_id=}. Manual update is required")
                print(f"Present in teams.csv but not in features: {current_info}🔚")
                print(f"Present in features but not in teams.csv: {new_info}🆕")
            
    teams_df.update(top_teams_df)
    teams_df.to_csv(teams_csv_path, index=False)
    
    if not problem:
        log_message(f"teams.csv is Up To Date ✅✅✅")
    else:
        print(f"⚠️ Update manually teams.csv with info above ⬆️")

    


    
