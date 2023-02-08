from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import json

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)



def get_listing_url():
    url_dict = {}
    for page_num in range(1,223,1):
        page_url = f"https://carsandbids.com/past-auctions/?page={page_num}"
        print(f"Scraping page {page_num}...")
    
        # def get_urls(page_url):           
        driver.get(page_url)
        time.sleep(10)
        page = driver.page_source
        
        soup = BeautifulSoup(page, 'html.parser')
        listing_urls = soup.find_all('div', class_='auction-title')

        
        for auction_url in listing_urls:
            url = auction_url.find('a').get('href')
            title = auction_url.find('a').get('title')
            url_dict[title] = f"https://carsandbids.com/{url}"
            
        time.sleep(10)
        print("Done!")
        
    # print(url_list)
    return url_dict
        
# get_listing_url()

def output(url_dict):
    with open('urls.json', 'w') as obj:
        json.dump(url_dict, obj, indent=4)


output(get_listing_url())