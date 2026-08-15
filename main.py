from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import os

# 1. Setup Chrome Driver
print("Setting up browser...")
options = Options()
options.add_argument("--headless") # run without opening chrome window
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

all_drugs = []
keywords = ["paracetamol", "metformin", "atorvastatin"]

# 2. Start Scraping
try:
    for keyword in keywords:
        print(f"\nScraping for: {keyword}")
        url = f"https://www.drugs.com/search.php?searchterm={keyword}&a=1"
        driver.get(url)
        time.sleep(4) # wait for website to load

        soup = BeautifulSoup(driver.page_source, 'lxml')
        results = soup.find_all('div', class_='ddc-media-content')

        for item in results[:10]: # take only 10 per keyword
            try:
                name = item.find('a').text.strip() if item.find('a') else 'N/A'
                desc = item.find('p').text.strip() if item.find('p') else 'N/A'
                all_drugs.append({
                    'drug_name': name,
                    'description': desc,
                    'search_keyword': keyword
                })
            except:
                continue
finally:
    driver.quit()
    print("\nBrowser closed.")

# 3. Pandas Cleaning
print(f"\nRaw data found: {len(all_drugs)}")
df = pd.DataFrame(all_drugs)

# Cleaning
df.drop_duplicates(subset=['drug_name'], inplace=True)
df['drug_name'] = df['drug_name'].str.title().str.strip()
df.fillna('Not Available', inplace=True)

# 4. Save
os.makedirs("data", exist_ok=True)
df.to_csv("data/pharma_data_cleaned.csv", index=False)
df.to_excel("data/pharma_data_cleaned.xlsx", index=False)

print("CLEANED DATA SAVED!")
print(df.head())