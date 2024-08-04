

def check_all_matches_has_exactly_10_rows(df):
    filtered_matches = df.groupby('match_id').filter(lambda x: len(x) < 10)

    corrupted_match_ids = filtered_matches['match_id'].unique()
    if corrupted_match_ids:
        print("❌ Match IDs with less than 10 rows:", corrupted_match_ids)
    else:
        print(f"all_players.csv (1/1).✅ All matches has exactly 10 rows")