from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
import locale
import csv
import os
import dotabet

def data_exists_in_csv(filename, data):
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            # Check if the date, league name, team 1, and team 2 are the same
            if (row[0] == data[0]) and (row[1] == data[1]) and (row[2] == data[2]) and (row[4] == data[4]):
                return True
    return False


def append_to_csv(filename, data):
    file_exists = os.path.isfile(filename)

    if not data_exists_in_csv(filename, data):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        return True
    else:
        print("❗Data already exist in CSV: ")
        return False

def get_date_ymd(block):
    today = datetime.today()
    tommorow_date = today + timedelta(days=1)
    
    date = block.text
    if date.split(' ')[0].split('\n')[0] == "TODAY":
        date_ymd = today.strftime('%Y-%m-%d')
    elif date.split(' ')[0] == "TOMORROW":
        date_ymd = tommorow_date.strftime('%Y-%m-%d')
    else:
        locale.setlocale(locale.LC_ALL, 'en_US')
        date_ymd = date_object = datetime.strptime(date, "%a, %b %d, %Y").strftime('%Y-%m-%d')
        print(f"Casting {date} -> {date_ymd}") 
    return date_ymd

def get_match_odds(block):
    participants = block.find_elements(By.CSS_SELECTOR, "div.style_gameInfoLabel__2m_fI > span")
    team_names = [p.text for p in participants if '(Match)' in p.text or '(Map 1)' in p.text]
    for p in participants:
        if '(Match)' in p.text:
            odd_type = '(Match)'
        elif '(Map 1)' in p.text:
            odd_type = '(Map 1)' 

    if team_names:
        money_line_buttons = block.find_elements(By.CSS_SELECTOR, "div.style_moneyline__2xTld > div > button")
        odds = []
        for btn in money_line_buttons:
            try:
                price_span = btn.find_element(By.CSS_SELECTOR, "span.style_price__3Haa9")
                odds.append(price_span.text)
            except NoSuchElementException:
                odds.append(None)
            
        team1, odd1 = team_names[0].split(odd_type)[0].strip(), odds[0]
        team2, odd2 = team_names[1].split(odd_type)[0].strip(), odds[1]
        team1, team2 = map(dotabet.utils.format_team_name, (team1, team2))
        rating1 = dotabet.utils.get_team_rating(team1)
        rating2 = dotabet.utils.get_team_rating(team2)
            
        return [team1, odd1, team2, odd2, odd_type, rating1, rating2]

def scrape_dota2_odds(debug=False):
    telegram_msg = []
    odds_file = r"D:\WORKSPACE\dotabet\data\odds\pinnacle.csv"

    chrome_driver_path = r"D:\PROGRAMS\chromedriver-win64\chromedriver.exe" # Update this to your path
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start browser maximized
    chrome_options.add_argument("--disable-infobars")  # Disables the "Chrome is being controlled by automated software" info bar
    chrome_options.add_argument("--disable-extensions")  # Disables extensions
    chrome_options.add_argument("--disable-gpu")  # Applicable to Windows OS only
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    # chrome_options.add_argument("--headless")  # Run browser in headless mode (without GUI)
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
    
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.pinnacle.com/en/esports/games/dota-2/matchups")
    time.sleep(5) 

    square = driver.find_element(By.CSS_SELECTOR, "div.contentBlock.square > div.contentBlock.square")
    content_blocks = square.find_elements(By.CSS_SELECTOR, "div[class^='style_']")

    attributes = ['style_dateBar__1adEH', 'style_row__yBzX8 style_row__3l5MS', 'style_row__yBzX8 style_row__12oAB']
    content_blocks = [cb for cb in content_blocks if cb.get_attribute("class") in attributes]
    n = len(content_blocks)

    for i, block in enumerate(content_blocks):
        if block.get_attribute("class") == 'style_dateBar__1adEH': # TODAY, TOMMOROW or DATE
            date_ymd = get_date_ymd(block)
            print(f"block[{i}/{n}]=Match_date: {date_ymd}")
            continue
        elif block.get_attribute("class") == "style_row__yBzX8 style_row__3l5MS": # LEAGUE NAME
            league_name = block.find_element(By.CSS_SELECTOR, "div.style_metadata__3MrIC > a > span").text
            print(f"block[{i}/{n}]=League_name: {league_name}")
            continue
        elif block.get_attribute("class") == "style_row__yBzX8 style_row__12oAB": # MATCH ODDS
            odd_data = get_match_odds(block)
            if odd_data and odd_data[1]: # (Match) or (Map 1) and non-empty
                data = [date_ymd, league_name] + odd_data + [None, None] # None for eloc1, eloc2 to pinnacle.csv
                if append_to_csv(odds_file, data):
                    telegram_msg.append(f"\n✅New:{data}")
                else:
                    telegram_msg.append("🔄")
                print(f"block[{i}/{n}]=Match_odds: {data=}")
            elif odd_data and not odd_data[1]: # (Match) but empty odds
                print(f"block[{i}/{n}] = (Match) but blocked odds🚫")
                telegram_msg.append("🚫")
            else:
                print(f"block[{i}/{n}]=<Skip non-(Match)> ")
        else:
            unknown_block = block.get_attribute("class")
            print(f"block {i}/{n} Unknown {unknown_block}")
    driver.quit()
    return telegram_msg
                