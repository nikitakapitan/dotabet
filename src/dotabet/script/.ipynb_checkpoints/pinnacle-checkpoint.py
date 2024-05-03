from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
import csv
import os

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
        print("❗Data already exist in CSV")
        return False

def scrape_dota2_odds():
    telegram_msg = ["New match parsed:"]
    
    odds_file = r"D:\WORKSPACE\dotabet\data\odds\pinnacle.csv"
    if not os.path.isfile(odds_file):
        with open(odds_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            header = ["Match_Date", "League_Name", "Team_1", "Odd_1", "Team_2", "Odd_2"]
            writer.writerow(header)
    
    today = datetime.today()
    today_date = today.strftime('%Y-%m-%d')
    tommorow_date = today + timedelta(days=1)
    
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # Navigate to the webpage
        driver.get("https://www.pinnacle.com/en/esports/games/dota-2/matchups")
    
        # Allow some time for the page to load
        time.sleep(5)  # Adjust time based on your internet speed
    
        # Find all content blocks that might contain match details for Today or Tomorrow
        date_blocks = driver.find_elements(By.CSS_SELECTOR, "div.contentBlock.square > div.contentBlock.square")
    
        for date_block in date_blocks:
            # Extract the date (e.g., Today, Tomorrow)
            date = date_block.find_element(By.CSS_SELECTOR, "div.style_dateBar__1adEH").text.split(' ')[0]
            if date.split('\n')[0] == "TODAY":
                date_ymd = today_date
            elif date.split('\n')[0] == "TOMMOROW":
                date_ymd = tommorow_date
            else:
                date_ymd = None
            
            # Find all league blocks within the date block
            league_blocks = date_block.find_elements(By.CSS_SELECTOR, "div.style_row__yBzX8.style_row__3l5MS")
    
            for league_block in league_blocks:
                # Extract the league name
                league_name = league_block.find_element(By.CSS_SELECTOR, "div.style_metadata__3MrIC > a > span").text
    
                # Extract match rows within the league block
                match_blocks = league_block.find_elements(By.XPATH, "following-sibling::div")
    
                for match in match_blocks:
                    # Stop if we hit another league block or end of date section
                    if match.get_attribute("class") == "style_row__yBzX8 style_row__3l5MS":
                        break
    
                    # Filter only rows with '(Match)' in the participant name
                    participants = match.find_elements(By.CSS_SELECTOR, "div.style_gameInfoLabel__2m_fI > span")
                    match_info = [p.text for p in participants if '(Match)' in p.text]
    
                    if match_info:
                        # Extract Money Line odds
                        money_line_buttons = match.find_elements(By.CSS_SELECTOR, "div.style_moneyline__2xTld > div > button")
                        odds = [btn.find_element(By.CSS_SELECTOR, "span.style_price__3Haa9").text for btn in money_line_buttons]

                        team1, odd1 = match_info[0].split(' (Match)')[0], odds[0]
                        team2, odd2 = match_info[1].split(' (Match)')[0], odds[1]
                        data = [date_ymd, league_name, team1, odd1, team2, odd2]
                        
                        print(f"{date_ymd=}\n {league_name=}\n {team1=} {odd1=} \n {team2=} {odd2=}\n----------\n")
                        
                        if append_to_csv(odds_file, data):
                            telegram_msg.append(f"🆕✅New:{data}")
                        else:
                            telegram_msg.append(f"🔄exist: {data}")
                        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up: close the browser
        driver.quit()
    return telegram_msg
