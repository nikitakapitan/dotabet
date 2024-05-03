from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import csv
import datetime
import time

def scrape_dota2_odds():
    info = []
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    # Target URL
    url = "https://www.bovada.lv/sports/esports/dota-2"
    driver.get(url)
    
    time.sleep(4)
    
    try:
        # Find the email field and send the email
        email_field = driver.find_element(By.ID, "email")
        email_field.send_keys("nickapch@gmail.com")
        
        # Find the password field and send the password
        password_field = driver.find_element(By.ID, "login-password")
        password_field.send_keys("P@r0lbovada")
        
        # Find and click the login button
        login_button = driver.find_element(By.ID, "login-submit")
        login_button.click()
    except:
        info.append('Login and password window didnt appear')
    

    # Wait for the login process to complete and for the next page to load
    time.sleep(10)
    
    # Extracting today's date to include in the CSV
    today_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Initialize CSV file writing
    with open(r"G:\My Drive\dotabet\odds\bovada_odds.csv", mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['Date', 'League Name', 'Team 1', 'Odd 1', 'Team 2', 'Odd 2', "Match Date"])
    
        # Extract all league sections
        leagues = driver.find_elements(By.CSS_SELECTOR, "div.grouped-events")
        for league in leagues:
            league_name = league.find_element(By.CSS_SELECTOR, "a.league-header-collapsible__description").text
            matches = league.find_elements(By.CSS_SELECTOR, "section.coupon-content")
            
            for match in matches:
                try:
                    # Time
                    match_date_span = match.find_elements(By.CSS_SELECTOR, "span.period.hidden-xs")
                    if match_date_span:
                        match_date_text = match_date_span[0].text.strip()
                        match_time_elements = match_date_span[0].find_elements(By.TAG_NAME, "time")
            
                        if match_time_elements:
                            match_time = match_time_elements[0].text.strip()
                            match_date = match_date_text.replace(match_time, '').strip()
                            full_date = f"{match_date} {match_time}"
                        else:
                            full_date = match_date_text
                    else:
                        full_date = "Date not found"
                
                    # Teams
                    teams = match.find_elements(By.CSS_SELECTOR, "div.competitors h4.competitor-name span.name")
                    team1_name = teams[0].text if len(teams) > 0 else 'N/A'
                    team2_name = teams[1].text if len(teams) > 1 else 'N/A'
                    
                    # Odds
                    odds = match.find_elements(By.CSS_SELECTOR, "button.bet-btn span.bet-price")
                    odd1 = odds[2].text if len(odds) > 2 else 'N/A'
                    odd2 = odds[3].text if len(odds) > 3 else 'N/A'
    
                    info.append(f'Writing f{[today_date, league_name, team1_name, odd1, team2_name, odd2, match_date_text]}')
                    writer.writerow([today_date, league_name, team1_name, odd1, team2_name, odd2, match_date_text])
                except Exception as e:
                    info.append(f"An error occurred: {e}")
    
    driver.quit()
    return info
