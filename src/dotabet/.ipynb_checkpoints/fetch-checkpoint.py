import json
import time
import requests

def fetch_data(url, max_retries=7, delay=10):
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request failed: {e}, attempt {attempt + 1}/{max_retries}. Retry in {delay} sec...")
            time.sleep(delay)
    print("Max retries exceeded.")
    return None