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
from dotabet.script.possibilities import possibilities

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

def get_match_odds(block, html_names):
    participants = block.find_elements(By.CSS_SELECTOR, html_names['game_info'])
    team_names = [p.text for p in participants if '(Match)' in p.text or '(Map 1)' in p.text]
    for p in participants:
        if '(Match)' in p.text:
            odd_type = '(Match)'
        elif '(Map 1)' in p.text:
            odd_type = '(Map 1)' 

    if team_names:
        money_line_buttons = block.find_elements(By.CSS_SELECTOR, html_names['button'])
        odds = []
        for btn in money_line_buttons:
            try:
                price_span = btn.find_element(By.CSS_SELECTOR, html_names['price'])
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
  
    current_html_names = {}
    for possible_html_name in possibilities:
        content_blocks_all = square.find_elements(By.CSS_SELECTOR, possible_html_name['html_class_name'])
        content_blocks = [cb for cb in content_blocks_all if cb.get_attribute("class") in possible_html_name['attributes'].values()]
        n = len(content_blocks)
        if content_blocks:
            print("HTML MATCH!")
            current_html_names = possible_html_name
            break

    for i, block in enumerate(content_blocks):
        if block.get_attribute("class") == current_html_names['attributes']['date']: # TODAY, TOMMOROW or DATE
            date_ymd = get_date_ymd(block)
            print(f"block[{i}/{n}]=Match_date: {date_ymd}")
            continue
        elif block.get_attribute("class") == current_html_names['attributes']['league']: # LEAGUE NAME
            league_name = block.find_element(By.CSS_SELECTOR, current_html_names['attributes']['league_name']).text
            print(f"block[{i}/{n}]=League_name: {league_name}")
            continue
        elif block.get_attribute("class") == current_html_names['attributes']['match']: # MATCH ODDS
            odd_data = get_match_odds(block, html_names=current_html_names['get_match_odds'])
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
                