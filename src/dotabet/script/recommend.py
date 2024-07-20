import pandas as pd

def elo_probability(rating1, rating2):
    return 1 / (1 + 10 ** ((rating2 - rating1) / 400))

def elo_coef(rating1, rating2):
    if rating1 and rating2:
        return 1/elo_probability(rating1, rating2)

def recommend_elo():
    telegram_msg = []
    pinnacle_path = r"D:\WORKSPACE\dotabet\data\odds\pinnacle.csv"
    df = pd.read_csv(pinnacle_path)

    df['eloc1'] = df.apply(lambda row: elo_coef(row['rating1'], row['rating2']), axis=1)
    df['eloc2'] = df.apply(lambda row: elo_coef(row['rating2'], row['rating1']), axis=1)

    df.to_csv(pinnacle_path, index=False)
    # ------------------------------------------------------------------------------------
    df['diff1'] = df['Odd_1'] - df['eloc1']
    df['diff2'] = df['Odd_2'] - df['eloc2']

    bets = []
    for idx, row in df.iterrows():
        if row['diff1'] > 0:
            bets.append((f"{row['Team_1']}", f"{row['Team_2']}", row['diff1'], row['Odd_1'], row['eloc1'], row['Match_Date'], row['League_Name']))
        if row['diff2'] > 0:
            bets.append((f"{row['Team_2']}", f"{row['Team_1']}", row['diff2'], row['Odd_2'], row['eloc2'], row['Match_Date'], row['League_Name']))

    bets_df = pd.DataFrame(bets, columns=['Favored', 'Opposed', 'Difference', 'BkMkr_odd', 'eloc_odd', 'match_date', 'league_name'])
    bets_df = bets_df.sort_values('Difference', ascending=False)
    
    telegram_msg = []
    for _, row in bets_df.iterrows():
        telegram_msg.append(f"💎Bet {row['Favored']} @ BkMkr:{row['BkMkr_odd']:.3f}(>Elo:{row['eloc_odd']:.3f}) vs {row['Opposed']} BkMkr +{100*(row['BkMkr_odd']/row['eloc_odd']-1):.2f}%\n📅 {row['match_date']} {row['league_name']} \n\n")


    return telegram_msg