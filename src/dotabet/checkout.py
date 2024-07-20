"""
This script:
Loads the D:\WORKSPACE\dotabet\data\odds\history.csv into df
Calculates the 'bet' Column: Determines which team to bet if bookmaker odds are higher than Elo. If no elo rating is available, set 'bet' to 0
Calculates the 'coef' Column: Determines the coefficient to bet on if public odds are higher than the ELO odds, or sets to 0 otherwise.
Calculates the 'result' Column: Evaluates the outcome of the bet based on the match winner and sets it to the coefficient if the bet was correct, -1 if incorrect, or False if no bet was placed.
Save results into new D:\WORKSPACE\dotabet\data\odds\results.csv
"""
import pandas as pd

def calculate_bet(row):
    if pd.isna(row['rating1']):
        return 0
    if row['Odd_1'] > row['eloc1']:
        return row['Team_1']
    if row['Odd_2'] > row['eloc2']:
        return row['Team_2']
    return 0

def calculate_coef(row):
    if row['Odd_1'] > row['eloc1']:
        return row['Odd_1']
    if row['Odd_2'] > row['eloc2']:
        return row['Odd_2']
    return 0

def calculate_result(row):
    if row['bet'] == 0:
        return False
    if row['winner'] == row['bet']:
        return row['coef'] - 1
    if isinstance(row['bet'], str):
        return -1
    return False

def compute_elo_results():
    df = pd.read_csv(r"D:\WORKSPACE\dotabet\data\odds\history.csv")
    df['bet'] = df.apply(calculate_bet, axis=1)
    df['coef'] = df.apply(calculate_coef, axis=1)
    df['result'] = df.apply(calculate_result, axis=1)
    df.to_csv(r"D:\WORKSPACE\dotabet\data\odds\elo_results.csv", index=False)
    return f"Balance: {df['result'].sum():.2f}"

